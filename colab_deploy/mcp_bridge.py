"""
Model Context Protocol (MCP) Server Bridge for Opal & Gemini Gems
"""
import sys
import json
import asyncio

async def handle_mcp_request(request_raw: str):
    try:
        req = json.loads(request_raw)
        method = req.get("method")
        req_id = req.get("id")

        if method == "tools/list":
            response = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": [
                        {
                            "name": "notebooklm_query_rag",
                            "description": "Query grounded vector sources from NotebookLM silo.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "notebook_id": {"type": "string"},
                                    "query": {"type": "string"}
                                },
                                "required": ["notebook_id", "query"]
                            }
                        }
                    ]
                }
            }
            print(json.dumps(response))
            sys.stdout.flush()
    except Exception as err:
        # Write errors to stderr to avoid crashing the MCP bridge loop
        sys.stderr.write(f"MCP Error: {err}\n")

async def main():
    while True:
        line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
        if not line:
            break
        await handle_mcp_request(line.strip())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
