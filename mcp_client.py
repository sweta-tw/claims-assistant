import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:

    def __init__(self):

        self.server_params = StdioServerParameters(
            command="python",
            args=["-m", "apps.mcp_server.server"],
        )

        self.read = None
        self.write = None
        self.session = None

    async def connect(self):

        self.stdio_context = stdio_client(
            self.server_params
        )

        self.read, self.write = await self.stdio_context.__aenter__()

        self.session = ClientSession(
            self.read,
            self.write
        )

        await self.session.__aenter__()

        await self.session.initialize()

    async def list_tools(self):

        response = await self.session.list_tools()

        return response.tools

    async def call_tool(
        self,
        tool_name,
        arguments
    ):

        return await self.session.call_tool(
            tool_name,
            arguments=arguments
        )

    async def close(self):

        if self.session:
            await self.session.__aexit__(
                None,
                None,
                None
            )

        if self.stdio_context:
            await self.stdio_context.__aexit__(
                None,
                None,
                None
            )