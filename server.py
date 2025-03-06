from mcp.server.fastmcp import FastMCP
import pixeltable as pxt
from typing import List, Dict, Any, Optional

# Create a named server
mcp = FastMCP("Pixeltable Assistant", dependencies=["pixeltable","sentence-transformers"])

@mcp.tool()
def list_tables() -> List[str]:
    """
    List all available pixeltable tables.
    
    Returns:
        List of table names
    """
    return pxt.list_tables()

@mcp.tool()
def create_table(path_str: str, schema: Dict[str, str]) -> str:
    """
    Create a new Pixeltable table with the provided schema.
    
    Args:
        path_str: The path/name of the table (e.g., 'mydir.mytable')
        schema: Dictionary of column_name: column_type pairs
               Valid types: 'String', 'Int', 'Float', 'Bool', 'Timestamp', 'Image', 'Video', 'Audio', 'Document', 'Json'
    
    Returns:
        Confirmation message
    """
    # Convert string types to actual Pixeltable types
    type_mapping = {
        'String': pxt.String,
        'Int': pxt.Int,
        'Float': pxt.Float,
        'Bool': pxt.Bool,
        'Timestamp': pxt.Timestamp,
        'Image': pxt.Image,
        'Video': pxt.Video,
        'Audio': pxt.Audio,
        'Document': pxt.Document,
        'Json': pxt.Json
    }
    
    typed_schema = {k: type_mapping.get(v, pxt.String) for k, v in schema.items()}
    
    try:
        table = pxt.create_table(path_str, typed_schema)
        return f"Successfully created table '{path_str}' with schema {schema}"
    except Exception as e:
        return f"Failed to create table: {str(e)}"

@mcp.tool()
def get_table_info(table_name: str) -> Dict[str, Any]:
    """
    Get information about a specific table including its schema.
    
    Args:
        table_name: Name of the table
    
    Returns:
        Dictionary with table information
    """
    try:
        table = pxt.get_table(table_name)
        if not table:
            return {"error": f"Table '{table_name}' not found"}
        
        schema = table.describe()
        return {
            "name": table_name,
            "schema": str(schema),
            "row_count": table.count()
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def insert_data(table_name: str, data: List[Dict[str, Any]]) -> str:
    """
    Insert data into a table.
    
    Args:
        table_name: Name of the table
        data: List of dictionaries containing the data to insert
    
    Returns:
        Confirmation message
    """
    try:
        table = pxt.get_table(table_name)
        if not table:
            return f"Table '{table_name}' not found"
        
        table.insert(data)
        return f"Successfully inserted {len(data)} row(s) into table '{table_name}'"
    except Exception as e:
        return f"Failed to insert data: {str(e)}"

@mcp.tool()
def query_table(table_name: str, limit: int = 10, where_clause: Optional[str] = None, 
                select_columns: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Query data from a table with optional filtering and column selection.
    
    Args:
        table_name: Name of the table
        limit: Maximum number of rows to return
        where_clause: Optional filter condition as a string (e.g., "column1 > 10")
        select_columns: Optional list of columns to select
    
    Returns:
        Dictionary with query results
    """
    try:
        table = pxt.get_table(table_name)
        if not table:
            return {"error": f"Table '{table_name}' not found"}
        
        # Start building the query
        query = table
        
        # Apply where clause if provided
        if where_clause:
            try:
                # This is a simplified approach - in reality, you'd need a more 
                # robust way to parse and evaluate the where clause
                query = eval(f"query.where({where_clause})")
            except Exception as e:
                return {"error": f"Invalid where clause: {str(e)}"}
        
        # Apply select columns if provided
        if select_columns:
            try:
                # Convert column names to table column references
                cols = [getattr(table, col) for col in select_columns]
                query = query.select(*cols)
            except Exception as e:
                return {"error": f"Invalid select columns: {str(e)}"}
        
        # Apply limit
        query = query.limit(limit)
        
        # Execute query and convert to list of dictionaries
        result = query.collect()
        result_data = []
        for row in result:
            row_dict = {}
            for i, column in enumerate(result.keys()):
                row_dict[column] = row[i]
            result_data.append(row_dict)
            
        return {
            "data": result_data,
            "count": len(result_data),
            "columns": list(result.keys())
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def add_computed_column(table_name: str, column_name: str, expression: str) -> str:
    """
    Add a computed column to a table.
    
    Args:
        table_name: Name of the table
        column_name: Name of the new computed column
        expression: Expression defining the computation (e.g., "table.column1 + table.column2")
    
    Returns:
        Confirmation message
    """
    try:
        table = pxt.get_table(table_name)
        if not table:
            return f"Table '{table_name}' not found"
        
        # This is a simplified approach - in reality, you'd need a more 
        # robust way to parse and evaluate the expression
        computed_value = eval(expression)
        
        # Add the computed column
        table.add_computed_column(**{column_name: computed_value})
        
        return f"Successfully added computed column '{column_name}' to table '{table_name}'"
    except Exception as e:
        return f"Failed to add computed column: {str(e)}"

@mcp.tool()
def create_view(view_name: str, table_name: str, iterator_type: Optional[str] = None, 
               iterator_params: Optional[Dict[str, Any]] = None) -> str:
    """
    Create a view from a table, optionally using an iterator.
    
    Args:
        view_name: Name for the new view
        table_name: Source table name
        iterator_type: Optional iterator type ('DocumentSplitter', 'FrameIterator', 'TileIterator', 'AudioSplitter')
        iterator_params: Optional parameters for the iterator
    
    Returns:
        Confirmation message
    """
    try:
        table = pxt.get_table(table_name)
        if not table:
            return f"Table '{table_name}' not found"
        
        # If no iterator is specified, create a simple view
        if not iterator_type:
            view = pxt.create_view(view_name, table)
            return f"Successfully created view '{view_name}' from table '{table_name}'"
        
        # Import the iterator
        iterator_params = iterator_params or {}
        
        if iterator_type == "DocumentSplitter":
            from pixeltable.iterators import DocumentSplitter
            iterator = DocumentSplitter.create(**iterator_params)
        elif iterator_type == "FrameIterator":
            from pixeltable.iterators import FrameIterator
            iterator = FrameIterator.create(**iterator_params)
        elif iterator_type == "TileIterator":
            from pixeltable.iterators import TileIterator
            iterator = TileIterator.create(**iterator_params)
        elif iterator_type == "AudioSplitter":
            from pixeltable.iterators import AudioSplitter
            iterator = AudioSplitter.create(**iterator_params)
        else:
            return f"Unknown iterator type: {iterator_type}"
        
        # Create view with the iterator
        view = pxt.create_view(view_name, table, iterator=iterator)
        return f"Successfully created view '{view_name}' from table '{table_name}' using {iterator_type}"
    except Exception as e:
        return f"Failed to create view: {str(e)}"

@mcp.tool()
def create_embedding_index(table_name: str, column_name: str, model_name: str = "all-MiniLM-L6-v2") -> str:
    """
    Create an embedding index on a column for similarity search.
    
    Args:
        table_name: Name of the table
        column_name: Name of the column to index
        model_name: Name of the embedding model
    
    Returns:
        Confirmation message
    """
    try:
        table = pxt.get_table(table_name)
        if not table:
            return f"Table '{table_name}' not found"
        
        from pixeltable.functions.huggingface import sentence_transformer
        
        # Create embedding function
        embed_model = sentence_transformer.using(model_id=f"sentence-transformers/{model_name}")
        
        # Add embedding index
        table.add_embedding_index(column_name, string_embed=embed_model)
        
        return f"Successfully created embedding index on column '{column_name}' in table '{table_name}'"
    except Exception as e:
        return f"Failed to create embedding index: {str(e)}"

@mcp.tool()
def similarity_search(table_name: str, column_name: str, query_text: str, limit: int = 5) -> Dict[str, Any]:
    """
    Perform a similarity search using an embedding index.
    
    Args:
        table_name: Name of the table
        column_name: Name of the column with the embedding index
        query_text: Text to search for
        limit: Maximum number of results to return
    
    Returns:
        Dictionary with search results
    """
    try:
        table = pxt.get_table(table_name)
        if not table:
            return {"error": f"Table '{table_name}' not found"}
        
        # Get the column
        column = getattr(table, column_name)
        
        # Calculate similarity
        sim = column.similarity(query_text)
        
        # Execute query
        result = table.order_by(sim, asc=False).limit(limit).select(
            "*", similarity=sim
        ).collect()
        
        # Convert to list of dictionaries
        result_data = []
        for row in result:
            row_dict = {}
            for i, column in enumerate(result.keys()):
                row_dict[column] = row[i]
            result_data.append(row_dict)
            
        return {
            "data": result_data,
            "count": len(result_data)
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def import_csv(table_path: str, csv_path: str) -> str:
    """
    Import data from a CSV file into a new table.
    
    Args:
        table_path: Path/name for the new table
        csv_path: Path to the CSV file
    
    Returns:
        Confirmation message
    """
    try:
        table = pxt.io.import_csv(table_path, csv_path)
        return f"Successfully imported CSV data into table '{table_path}'"
    except Exception as e:
        return f"Failed to import CSV: {str(e)}"

@mcp.tool()
def create_directory(dir_name: str) -> str:
    """
    Create a directory to organize tables.
    
    Args:
        dir_name: Name of the directory
    
    Returns:
        Confirmation message
    """
    try:
        pxt.create_dir(dir_name, if_exists="ignore")
        return f"Successfully created directory '{dir_name}'"
    except Exception as e:
        return f"Failed to create directory: {str(e)}"

if __name__ == "__main__":
    mcp.run()