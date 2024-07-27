# from sqlmodel import SQLModel, Session, create_engine
from contextlib import asynccontextmanager
import os
from fastapi import HTTPException
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from model import Subtitle
from util import request_video_info


@asynccontextmanager
async def get_session():
    postgres_url = os.environ.get("COCKROACHDB_ASYNC")  
    engine = create_async_engine(postgres_url, echo=True, pool_pre_ping=True)
    async with AsyncSession(engine) as session:
        try:
            yield session
        finally:
            await session.close()
        await engine.dispose()

async def get_db():
    async with get_session() as session:
        yield session

async def insert_video_sub(session: AsyncSession, video_id, zh_txt=None, en_txt=None, video_topic=None, playlist_id=None):
    video_title, channel_id, channel_name, language = None, None, None, None
    content_topic = video_topic or None
    video_info = request_video_info(video_id)
    if video_info:
        video_title = video_info['title']
        channel_id = video_info['channelId']
        channel_name = video_info['channelTitle']
        default_audio_language = video_info['defaultAudioLanguage']
        language = 'zh' if (default_audio_language == 'zh' or default_audio_language == 'zh-TW') else 'en-zh'

        if default_audio_language == 'en' and en_txt == None:
            en_transcript = YouTubeTranscriptApi.get_transcript(video_id)
            en_txt = TextFormatter().format_transcript(en_transcript)
        
        new_sub = Subtitle(video_id=video_id, video_title=video_title, lang_code=language, channel_id=channel_id, channel_name=channel_name, zh_subtitle=zh_txt, en_subtitle=en_txt, playlist_id=playlist_id, content_topic=content_topic)
        session.add(new_sub)
        try:
            await session.commit()
            await session.refresh(new_sub)
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=f"An error occurred while adding the item: {str(e)}")