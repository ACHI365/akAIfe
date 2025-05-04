
import asyncio
import sys
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env
class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
        self.messages = []  # To store the message history

    async def connect_to_server(self, server_script_path: str):
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        # Add the user's query to the message history
        self.messages.append({"role": "user", "content": query})

        # Create the messages list with the full conversation history
        messages = self.messages

        # List available tools
        response = await self.session.list_tools()
        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]

        # Define the system prompt
        system_prompt = {
            "role": "user",
            "content": [{
                "type": "text",
                "text": "You are a trip advisor. Always try to answer simply and do not ask additional data if not necessary."
            }]
        }

        final_text = []
        while True:
            # Call the Anthropics API with full message history
            response = self.anthropic.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=20000,
                temperature=0.7,
                messages=[system_prompt] + messages,
                tools=available_tools
            )

            used_tool = False
            for content in response.content:
                if content.type == 'text':
                    final_text.append(content.text)
                    # Add the assistant's response to the message history
                    self.messages.append({"role": "assistant", "content": content.text})
                elif content.type == 'tool_use':
                    used_tool = True
                    tool_name = content.name
                    tool_args = content.input
                    result = await self.session.call_tool(tool_name, tool_args)
                    # Add the result to the conversation history
                    self.messages.append({
                        "role": "user",
                        "content": result.content
                    })
                    final_text.append(f"[Tool: {tool_name} | Args: {tool_args} | Result: {result.content}]")

            if not used_tool:
                break

        return "\n".join(final_text)

    async def chat_loop(self):
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
