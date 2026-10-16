import asyncio

from mcp_client import MCPClient


async def main():

    client = MCPClient()

    try:

        await client.connect()

        tools = await client.list_tools()

        print("\nAvailable tools:")

        for tool in tools:
            print(f"- {tool.name}")
            print(f"  Description: {tool.description}")
            print("Input schema:", tool.input_schema)

        result = await client.call_tool(
            "get_claim",
            {
                "claim_id": "CLM-1001"
            }
        )

        print("\nResult:")
        print(result)

    finally:

        await client.close()


if __name__ == "__main__":
    asyncio.run(main())