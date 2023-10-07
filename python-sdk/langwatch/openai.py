from typing import Any, AsyncGenerator, Dict, Generator, List, Optional, Union, cast
import openai
from langwatch.tracer import BaseTracer

from langwatch.types import (
    ErrorCapture,
    StepInput,
    StepMetrics,
    StepOutput,
    StepOutputText,
    StepParams,
    StepTimestamps,
    StepTrace,
)
from langwatch.utils import (
    capture_async_chunks_with_timings_and_reyield,
    capture_chunks_with_timings_and_reyield,
    capture_exception,
    milliseconds_timestamp,
    safe_get,
)


class OpenAICompletionTracer(BaseTracer):
    def __enter__(self):
        super().__enter__()
        self._original_completion_create = openai.Completion.create
        self._original_completion_acreate = openai.Completion.acreate

        openai.Completion.create = self.patched_completion_create
        openai.Completion.acreate = self.patched_completion_acreate

    def __exit__(self, _type, _value, _traceback):
        super().__exit__(_type, _value, _traceback)
        openai.Completion.create = self._original_completion_create

    def patched_completion_create(self, *args, **kwargs):
        requested_at = milliseconds_timestamp()
        try:
            response = self._original_completion_create(*args, **kwargs)

            if isinstance(response, Generator):
                return capture_chunks_with_timings_and_reyield(
                    response,
                    lambda chunks, first_token_at, finished_at: self.handle_deltas(
                        chunks,
                        StepTimestamps(
                            requested_at=requested_at,
                            first_token_at=first_token_at,
                            finished_at=finished_at,
                        ),
                        **kwargs,
                    ),
                )
            else:
                finished_at = milliseconds_timestamp()
                self.handle_list_or_dict(
                    response,
                    StepTimestamps(requested_at=requested_at, finished_at=finished_at),
                    **kwargs,
                )
                return response
        except Exception as err:
            finished_at = milliseconds_timestamp()
            self.handle_exception(
                err,
                StepTimestamps(requested_at=requested_at, finished_at=finished_at),
                **kwargs,
            )
            raise err

    async def patched_completion_acreate(self, *args, **kwargs):
        requested_at = milliseconds_timestamp()
        response = await self._original_completion_acreate(*args, **kwargs)

        if isinstance(response, AsyncGenerator):
            return capture_async_chunks_with_timings_and_reyield(
                response,
                lambda chunks, first_token_at, finished_at: self.handle_deltas(
                    chunks,
                    StepTimestamps(
                        requested_at=requested_at,
                        first_token_at=first_token_at,
                        finished_at=finished_at,
                    ),
                    **kwargs,
                ),
            )
        else:
            finished_at = milliseconds_timestamp()
            self.handle_list_or_dict(
                response,
                StepTimestamps(requested_at=requested_at, finished_at=finished_at),
                **kwargs,
            )
            return response

    def handle_deltas(
        self,
        deltas: List[Union[Dict[Any, Any], List[Any]]],
        timestamps: StepTimestamps,
        **kwargs,
    ):
        raw_response = []
        text_outputs: Dict[int, str] = {}
        for delta in deltas:
            delta = cast(Dict[Any, Any], delta)
            raw_response.append(delta)
            for choice in delta.get("choices", []):
                index = choice.get("index", 0)
                text_outputs[index] = text_outputs.get(index, "") + choice.get(
                    "text", ""
                )

        self.steps.append(
            self.build_trace(
                raw_response=raw_response,
                outputs=[
                    StepOutputText(type="text", value=output)
                    for output in text_outputs.values()
                ],
                metrics=StepMetrics(),
                timestamps=timestamps,
                error=None,
                **kwargs,
            )
        )

    def handle_list_or_dict(
        self,
        res: Union[List[Any], Dict[Any, Any]],
        timestamps: StepTimestamps,
        **kwargs,
    ):
        responses_list: List[dict] = res if isinstance(res, list) else [res]
        for response in responses_list:
            self.steps.append(
                self.build_trace(
                    raw_response=response,
                    outputs=[
                        StepOutputText(type="text", value=output.get("text"))
                        for output in response.get("choices", [])
                    ],
                    metrics=StepMetrics(
                        prompt_tokens=safe_get(response, "usage", "prompt_tokens"),
                        completion_tokens=safe_get(
                            response, "usage", "completion_tokens"
                        ),
                    ),
                    timestamps=timestamps,
                    error=None,
                    **kwargs,
                )
            )

    def handle_exception(
        self,
        err: Exception,
        timestamps: StepTimestamps,
        **kwargs,
    ):
        self.steps.append(
            self.build_trace(
                raw_response=None,
                outputs=[],
                metrics=StepMetrics(),
                timestamps=timestamps,
                error=capture_exception(err),
                **kwargs,
            )
        )

    def build_trace(
        self,
        raw_response: Optional[Union[dict, list]],
        outputs: List[StepOutput],
        metrics: StepMetrics,
        timestamps: StepTimestamps,
        error: Optional[ErrorCapture],
        **kwargs,
    ) -> StepTrace:
        return StepTrace(
            trace_id=self.trace_id,
            model=f"openai/{kwargs.get('model', 'unknown')}",
            input=StepInput(type="text", value=kwargs.get("prompt") or ""),
            outputs=outputs,
            raw_response=raw_response,
            error=error,
            params=StepParams(
                temperature=kwargs.get("temperature", 1.0),
                stream=kwargs.get("stream", False),
            ),
            metrics=metrics,
            timestamps=timestamps,
        )