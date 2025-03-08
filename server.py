from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server import Server
import uvicorn

import pixeltable as pxt

mcp = FastMCP("Pixeltable")

@mcp.tool()
def create_table(table_name: str, columns: dict[str, str]) -> str:
    """Create a table in Pixeltable.
    
    Args:
        table_name: The name of the table to create.
        columns: A dictionary of column names and types.
    
    Eligible column types: 

    from .type_system import (
        Array,
        Audio,
        Bool,
        Document,
        Float,
        Image,
        Int,
        Json,
        Required,
        String,
        Timestamp,
        Video,
    )

    Example:
    columns = {
        "name": String,
        "age": Int,
        "is_active": Bool,
    }

    """
    # Map string type names to actual Pixeltable types
    type_mapping = {
        "array": pxt.Array,
        "audio": pxt.Audio,
        "bool": pxt.Bool,
        "document": pxt.Document,
        "float": pxt.Float,
        "image": pxt.Image,
        "int": pxt.Int,
        "json": pxt.Json,
        "required": pxt.Required,
        "string": pxt.String,
        "timestamp": pxt.Timestamp,
        "video": pxt.Video,
    }
    
    # Convert string type names to actual type objects
    converted_columns = {}
    for col_name, col_type in columns.items():
        col_type_lower = col_type.lower()
        if col_type_lower in type_mapping:
            converted_columns[col_name] = type_mapping[col_type_lower]
        else:
            return f"Invalid column type: {col_type}. Valid types are: {', '.join(type_mapping.keys())}"
    
    pxt.create_table(table_name, schema_or_df=converted_columns, if_exists="replace")
    if table_name in pxt.list_tables():
        return f"Table {table_name} created successfully."
    else:
        return f"Table {table_name} creation failed."

@mcp.tool()
def insert_data(table_name: str, data: list[dict]) -> str:
    """Insert data into a table in Pixeltable.
    
    Args:
        table_name: The name of the table to insert data into.
        data: A list of dictionaries, each representing a row of data.
        The keys of the dictionary should match the column names and types of the table.
    """
    table = pxt.get_table(table_name)
    table.insert(data)
    return f"Data inserted successfully."

def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can server the provied mcp server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,  # noqa: SLF001
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


if __name__ == "__main__":
    mcp_server = mcp._mcp_server  # noqa: WPS437

    import argparse
    
    parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on')
    args = parser.parse_args()

    starlette_app = create_starlette_app(mcp_server, debug=True)
    uvicorn.run(starlette_app, host=args.host, port=args.port)
