from mcp.server.fastmcp import FastMCP
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
