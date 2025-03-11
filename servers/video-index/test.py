from datetime import datetime
import pixeltable as pxt
from pixeltable.functions import openai
from pixeltable.functions.huggingface import sentence_transformer
from pixeltable.functions.video import extract_audio
from pixeltable.iterators import AudioSplitter
from pixeltable.iterators.string import StringSplitter

DIRECTORY = 'video_index'
TABLE_NAME = f'{DIRECTORY}.video'
CHUNKS_VIEW_NAME = f'{DIRECTORY}.video_chunks'
SENTENCES_VIEW_NAME = f'{DIRECTORY}.video_sentence_chunks'
WHISPER_MODEL = 'whisper-1'
DELETE_INDEX = True

if DELETE_INDEX and TABLE_NAME in pxt.list_tables():
    pxt.drop_dir(DIRECTORY, force=True)

if TABLE_NAME not in pxt.list_tables():
    # Create video table
    pxt.create_dir(DIRECTORY, if_exists='ignore')
    video_index = pxt.create_table(TABLE_NAME, {'video': pxt.Video, 'uploaded_at': pxt.Timestamp})

    # Video-to-audio
    video_index.add_computed_column(audio_extract=extract_audio(video_index.video, format='mp3'))

    # Create view for audio chunks
    chunks_view = pxt.create_view(
        CHUNKS_VIEW_NAME,
        video_index,
        iterator=AudioSplitter.create(
            audio=video_index.audio_extract,
            chunk_duration_sec=30.0,
            overlap_sec=2.0,
            min_chunk_duration_sec=5.0
        )
    )

    # Audio-to-text for chunks
    chunks_view.add_computed_column(
        transcription=openai.transcriptions(audio=chunks_view.audio_chunk, model=WHISPER_MODEL)
    )

    # Create view that chunks text into sentences
    transcription_chunks = pxt.create_view(
        SENTENCES_VIEW_NAME,
        chunks_view,
        iterator=StringSplitter.create(text=chunks_view.transcription.text, separators='sentence'),
    )

    # Define the embedding model
    embed_model = sentence_transformer.using(model_id='intfloat/e5-large-v2')

    # Create embedding index
    transcription_chunks.add_embedding_index('text', string_embed=embed_model)

else:
    video_index = pxt.get_table(TABLE_NAME)
    chunks_view = pxt.get_table(CHUNKS_VIEW_NAME)
    transcription_chunks = pxt.get_table(SENTENCES_VIEW_NAME)

# Insert Videos
videos = [
    'https://github.com/pixeltable/pixeltable/raw/release/docs/resources/audio-transcription-demo/'
    f'Lex-Fridman-Podcast-430-Excerpt-{n}.mp4'
    for n in range(3)
]

video_index.insert({'video': video, 'uploaded_at': datetime.now()} for video in videos[:2])

# Query the table
sim = transcription_chunks.text.similarity('What is happiness?')

print(
    transcription_chunks.order_by(sim, transcription_chunks.uploaded_at, asc=False)
    .limit(5)
    .select(transcription_chunks.text, transcription_chunks.uploaded_at, similarity=sim)
    .collect()
)