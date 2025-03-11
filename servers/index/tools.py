import pixeltable as pxt
import os
from mcp.server.fastmcp import FastMCP
from pixeltable.functions import whisper
from pixeltable.functions.huggingface import sentence_transformer
from pixeltable.iterators.string import StringSplitter
from pixeltable.iterators import AudioSplitter

mcp = FastMCP("Pixeltable")

# Base directory for all indexes
DIRECTORY = 'audio_index'

# Registry to hold all audio indexes
audio_indexes = {}

@mcp.tool()
def setup_audio_index(table_name: str, openai_api_key: str) -> str:
    """Set up an audio index with the provided name and OpenAI API key.

    Args:
        table_name: The name of the audio index (e.g., 'podcasts', 'interviews').
        openai_api_key: The OpenAI API key required for Whisper transcription.

    Returns:
        A message indicating whether the index was created, already exists, or failed.
    """
    global audio_indexes
    try:
        # Set the API key
        os.environ['OPENAI_API_KEY'] = openai_api_key

        # Construct full table and view names
        full_table_name = f'{DIRECTORY}.{table_name}'
        chunks_view_name = f'{DIRECTORY}.{table_name}_chunks'
        sentences_view_name = f'{DIRECTORY}.{table_name}_sentence_chunks'

        # Check if the table already exists
        existing_tables = pxt.list_tables()
        if full_table_name in existing_tables:
            audio_index = pxt.get_table(full_table_name)
            chunks_view = pxt.get_view(chunks_view_name)
            sentences_view = pxt.get_view(sentences_view_name)
            audio_indexes[full_table_name] = (audio_index, chunks_view, sentences_view)
            return f"Audio index '{full_table_name}' already exists and is ready for use."

        # Create directory and table
        pxt.create_dir(DIRECTORY, if_exists='ignore')
        audio_index = pxt.create_table(full_table_name, {'audio_file': pxt.Audio}, if_exists='ignore')

        # Create view for audio chunks
        chunks_view = pxt.create_view(
            chunks_view_name,
            audio_index,
            iterator=AudioSplitter.create(
                audio=audio_index.audio_file,
                chunk_duration_sec=30.0,
                overlap_sec=2.0,
                min_chunk_duration_sec=5.0
            ),
            if_exists='ignore'
        )

        # Add transcription to chunks
        chunks_view.add_computed_column(
            transcription=whisper.transcribe(audio=chunks_view.audio_chunk, model='base.en')
        )

        # Create view that chunks transcriptions into sentences
        sentences_view = pxt.create_view(
            sentences_view_name,
            chunks_view,
            iterator=StringSplitter.create(text=chunks_view.transcription.text, separators='sentence'),
            if_exists='ignore'
        )

        # Define the embedding model and create embedding index
        embed_model = sentence_transformer.using(model_id='intfloat/e5-large-v2')
        sentences_view.add_embedding_index(column='text', string_embed=embed_model)

        # Store in the registry
        audio_indexes[full_table_name] = (audio_index, chunks_view, sentences_view)
        return f"Audio index '{full_table_name}' created successfully."
    except Exception as e:
        return f"Error setting up audio index '{full_table_name}': {str(e)}"

@mcp.tool()
def insert_audio(table_name: str, audio_location: str) -> str:
    """Insert an audio file into the specified audio index.

    Args:
        table_name: The name of the audio index (e.g., 'podcasts', 'interviews').
        audio_location: The URL or path to the audio file to insert (e.g., local path or S3 URL).

    Returns:
        A confirmation message indicating success or failure.
    """
    full_table_name = f'{DIRECTORY}.{table_name}'
    try:
        if full_table_name not in audio_indexes:
            return f"Error: Audio index '{full_table_name}' not set up. Please call setup_audio_index first."
        audio_index, _, _ = audio_indexes[full_table_name]
        audio_index.insert([{'audio_file': audio_location}])
        return f"Audio file '{audio_location}' inserted successfully into index '{full_table_name}'."
    except Exception as e:
        return f"Error inserting audio file into '{full_table_name}': {str(e)}"

@mcp.tool()
def query_audio(table_name: str, query_text: str, top_n: int = 5) -> str:
    """Query the specified audio index with a text question.

    Args:
        table_name: The name of the audio index (e.g., 'podcasts', 'interviews').
        query_text: The question or text to search for in the audio content.
        top_n: Number of top results to return (default is 5).

    Returns:
        A string containing the top matching sentences and their similarity scores.
    """
    full_table_name = f'{DIRECTORY}.{table_name}'
    try:
        if full_table_name not in audio_indexes:
            return f"Error: Audio index '{full_table_name}' not set up. Please call setup_audio_index first."
        _, _, sentences_view = audio_indexes[full_table_name]
        # Calculate similarity scores between query and sentences
        sim = sentences_view.text.similarity(query_text)

        # Get top results
        results = (sentences_view.order_by(sim, asc=False)
                  .select(sentences_view.text, sim=sim, audio_file=sentences_view.audio_file)
                  .limit(top_n)
                  .collect())

        # Format the results
        result_str = f"Query Results for '{query_text}' in '{full_table_name}':\n\n"
        for i, row in enumerate(results.to_pandas().itertuples(), 1):
            result_str += f"{i}. Score: {row.sim:.4f}\n"
            result_str += f"   Text: {row.text}\n"
            result_str += f"   From audio: {row.audio_file}\n\n"
        
        return result_str if result_str else "No results found."
    except Exception as e:
        return f"Error querying audio index '{full_table_name}': {str(e)}"

@mcp.tool()
def list_tables() -> str:
    """List all audio indexes currently available.

    Returns:
        A string listing the current audio indexes.
    """
    tables = pxt.list_tables()
    audio_tables = [t for t in tables if t.startswith(f'{DIRECTORY}.')]
    return f"Current audio indexes: {', '.join(audio_tables)}" if audio_tables else "No audio indexes exist."