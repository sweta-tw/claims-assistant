import asyncio
import json

from mcp_client import MCPClient
from llm_client import LLMClient


MAX_ITERATIONS = 1


def convert_mcp_tools(mcp_tools):
    """
    Convert MCP tool definitions into
    OpenAI Responses API tool format.
    """

    tools = []

    for tool in mcp_tools:
        tools.append({
            "type": "function",
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.input_schema
        })

    return tools


async def execute_tool_call(mcp_client, tool_call):
    """
    Execute one tool requested by the LLM.
    """

    tool_name = tool_call.name

    arguments = json.loads(
        tool_call.arguments
    )

    print("\n--------------------------------")
    print("Executing MCP tool")
    print("--------------------------------")

    print("Tool:", tool_name)
    print("Arguments:", arguments)

    result = await mcp_client.call_tool(
        tool_name,
        arguments
    )

    print("\nMCP result:")
    print(result)

    return result


async def main():

    mcp_client = MCPClient()
    llm_client = LLMClient()

    try:

        # ==================================================
        # 1. CONNECT TO MCP SERVER
        # ==================================================

        print("\nConnecting to MCP server...")

        await mcp_client.connect()

        print("Connected to MCP server.")


        # ==================================================
        # 2. DISCOVER MCP TOOLS
        # ==================================================

        mcp_tools = await mcp_client.list_tools()

        print("\nAvailable MCP tools:")

        for tool in mcp_tools:
            print(
                f"- {tool.name}: "
                f"{tool.description}"
            )


        # ==================================================
        # 3. CONVERT MCP TOOLS
        # ==================================================

        llm_tools = convert_mcp_tools(
            mcp_tools
        )


        # ==================================================
        # 4. USER INPUT
        # ==================================================

        messages = [
            {
                "role": "user",
                "content": (
                    "Get the status of CLM-1001 and if it is SUBMITTED, move it to UNDER_REVIEW."
                )
            }
        ]


        # ==================================================
        # 5. AGENT LOOP
        # ==================================================

        for iteration in range(MAX_ITERATIONS):

            print(
                f"\n========== AGENT ITERATION "
                f"{iteration + 1} =========="
            )


            # --------------------------------------------------
            # Ask GPT-5 nano
            # --------------------------------------------------

            response = llm_client.chat(
                messages,
                tools=llm_tools
            )

            print(response , 'response1')


            # --------------------------------------------------
            # Find function calls
            # --------------------------------------------------

            tool_calls = [
                item
                for item in response.output
                if item.type == "function_call"
            ]

            print(tool_calls , 'tool_calls1')


            # ==================================================
            # 6. NO TOOL CALL → FINAL ANSWER
            # ==================================================

            if not tool_calls:

                print("\n================================")
                print("FINAL ANSWER")
                print("================================")

                print(response.output_text)

                break


            # ==================================================
            # 7. EXECUTE TOOL CALLS
            # ==================================================

            for tool_call in tool_calls:

                result = await execute_tool_call(
                    mcp_client,
                    tool_call
                )


                # --------------------------------------------------
                # Add the model's function call to the conversation
                # --------------------------------------------------

                messages.append({
                    "type": "function_call",
                    "call_id": tool_call.call_id,
                    "name": tool_call.name,
                    "arguments": tool_call.arguments
                })


                # --------------------------------------------------
                # Add tool result to the conversation
                # --------------------------------------------------

                messages.append({
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": str(result)
                })


        # ==================================================
        # 8. MAX ITERATIONS REACHED
        # ==================================================

        else:

            print(
                "\nAgent stopped because "
                "maximum iterations were reached."
            )


    finally:

        # ==================================================
        # 9. CLOSE MCP CONNECTION
        # ==================================================

        await mcp_client.close()


if __name__ == "__main__":
    asyncio.run(main())