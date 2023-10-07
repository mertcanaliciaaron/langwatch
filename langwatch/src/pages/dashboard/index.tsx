import {
  Box,
  Checkbox,
  HStack,
  Input,
  Spacer,
  Tag,
  VStack,
} from "@chakra-ui/react";
import {
  type Icon,
  Search,
  User,
  Bell,
  Activity,
  Settings,
  Filter,
  Check,
} from "react-feather";

export default function Dashboard() {
  const MenuButton = ({ icon, label }: { icon: Icon; label: string }) => {
    const IconElem = icon;
    return (
      <a href="#">
        <VStack>
          <IconElem size={42} />
          <Box fontSize={16}>{label}</Box>
        </VStack>
      </a>
    );
  };

  const Message = () => {
    return (
      <VStack
        alignItems="flex-start"
        padding={6}
        spacing={4}
        borderBottom="1px solid #E5E5E5"
      >
        <HStack spacing={12} width="full">
          <Box fontSize={24} fontWeight="bold">
            What is up
          </Box>
          <Spacer />
          <Box>1273 tokens</Box>
          <Box>10s ago</Box>
        </HStack>
        <p>
          Hey there, I’m an AI assistant lorem ipsum dolor sit amet, consectetur
          adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore
          magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation
          ullamco laboris nisi ut aliquip ex ea commodo consequat...
        </p>
        <HStack marginTop={1}>
          <Check size={16} />
          <Box>No PII leak</Box>
        </HStack>
        <HStack>
          <Tag size="md">Greeting</Tag>
          <Tag>Small Talk</Tag>
        </HStack>
      </VStack>
    );
  };

  return (
    <HStack width="full" minHeight="100vh" alignItems={"stretch"} spacing={0}>
      <Box borderRight="1px solid #E5E5E5">
        <VStack
          paddingX={16}
          paddingY={8}
          spacing={16}
          position="sticky"
          top={0}
        >
          <Box fontSize={32} fontWeight="bold">
            LO
            <br />
            GO
          </Box>
          <VStack spacing={8}>
            <MenuButton icon={Search} label="Search" />
            <MenuButton icon={User} label="Users" />
            <MenuButton icon={Activity} label="Analytics" />
            <MenuButton icon={Bell} label="Alerts" />
            <MenuButton icon={Settings} label="Settings" />
          </VStack>
        </VStack>
      </Box>
      <VStack width="full" spacing={0}>
        <VStack
          width="full"
          spacing={0}
          position="sticky"
          top={0}
          background="white"
        >
          <Box position="relative" width="full">
            <Box position="absolute" top={6} left={6}>
              <Search size={16} />
            </Box>
            <Input
              variant="unstyled"
              placeholder={"Search"}
              padding={5}
              paddingLeft={12}
              borderRadius={0}
              borderBottom="1px solid #E5E5E5"
            />
          </Box>
          <HStack
            paddingY={5}
            paddingX={6}
            spacing={12}
            width="full"
            borderBottom="1px solid #E5E5E5"
          >
            <Filter size={24} />
            <Spacer />
            <Checkbox>Inbox Narrator</Checkbox>
            <Checkbox>All models</Checkbox>
            <Checkbox>Last 7 days</Checkbox>
          </HStack>
        </VStack>
        <Message />
        <Message />
        <Message />
        <Message />
        <Message />
        <Message />
        <Message />
        <Message />
      </VStack>
    </HStack>
  );
}