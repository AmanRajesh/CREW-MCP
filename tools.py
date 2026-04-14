import asyncio
from crewai.tools import BaseTool
from contextlib import AsyncExitStack
from mcp import ClientSession
from mcp.client.sse import sse_client
from pydantic import BaseModel, Field

# 1. Define the input schemas FIRST
class SearchManualInput(BaseModel):
    """Input schema for searching the technical manual."""
    symptom_or_error: str = Field(..., description="The symptom description or error code found on the device.")

class CheckInventoryInput(BaseModel):
    """Input schema for checking hospital inventory."""
    part_number: str = Field(..., description="The exact SKU/part number extracted from the manual.")

# Ensure the MCP Server is running before these tools are called!

class MCPSearchManualTool(BaseTool):
    name: str = "search_technical_manual"
    description: str = "Searches the unstructured technical manual for the given symptom or error code and returns the SKU and required safety precautions."
    args_schema: type[BaseModel] = SearchManualInput # Added schema for consistency
    
    def _run(self, symptom_or_error: str) -> str:
        return asyncio.run(self._call_mcp(symptom_or_error))

    async def _call_mcp(self, symptom_or_error: str) -> str:
        async with AsyncExitStack() as stack:
            try:
                # Target the SSE transport on Port 8080
                read, write = await stack.enter_async_context(sse_client("http://localhost:8080/sse"))
                session = await stack.enter_async_context(ClientSession(read, write))
                await session.initialize()
                
                result = await session.call_tool("search_technical_manual", arguments={"symptom_or_error": symptom_or_error})
                return result.content[0].text
            except Exception as e:
                return f"Error communicating with MCP server: {e}"

class MCPCheckInventoryTool(BaseTool):
    name: str = "check_hospital_inventory"
    description: str = "Checks the hospital inventory database for stock levels and unit cost for a given part number."
    args_schema: type[BaseModel] = CheckInventoryInput # Now this works because it's defined above
    
    def _run(self, part_number: str) -> str:
        return asyncio.run(self._call_mcp(part_number))

    async def _call_mcp(self, part_number: str) -> str:
        async with AsyncExitStack() as stack:
            try:
                read, write = await stack.enter_async_context(sse_client("http://localhost:8080/sse"))
                session = await stack.enter_async_context(ClientSession(read, write))
                await session.initialize()
                
                result = await session.call_tool("check_hospital_inventory", arguments={"part_number": part_number})
                return result.content[0].text
            except Exception as e:
                return f"Error communicating with MCP server: {e}"