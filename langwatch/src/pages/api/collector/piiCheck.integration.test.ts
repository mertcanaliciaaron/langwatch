import { describe, expect, it } from "vitest";
import type { Trace } from "../../../server/tracer/types";
import { cleanupPIIs } from "./piiCheck";

describe("PIICheck", () => {
  it("detects PII on traces", async () => {
    const sampleTrace: Trace = {
      trace_id: "foo",
      project_id: "foo",
      metadata: {},
      input: { value: "hi there" },
      metrics: {},
      timestamps: { started_at: Date.now(), inserted_at: Date.now() },
    };
    await cleanupPIIs(sampleTrace, [], false);
    expect(sampleTrace.input.value).toEqual("hi there");

    const samplePIITrace: Trace = {
      trace_id: "foo",
      project_id: "foo",
      metadata: {},
      input: {
        value: "hi there, my credit card number is 4012-8888-8888-1881",
      },
      metrics: {},
      timestamps: { started_at: Date.now(), inserted_at: Date.now() },
    };

    await cleanupPIIs(samplePIITrace, [], false);
    expect(samplePIITrace.input.value).toEqual(
      "hi there, my credit card number is [REDACTED]"
    );
  });
});
