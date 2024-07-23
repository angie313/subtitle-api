from sqlmodel import SQLModel, Session, create_engine
import os
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

from model import Subtitle
from util import request_video_info

def init_engine():
    postgres_url = os.environ.get("COCKROACHDB_URL", None)
    if postgres_url:
        engine = create_engine(postgres_url, echo=True)
        return engine
    else:
        print("Postgresql URL not found!")
        return None

# Need to import model class for table creation
def create_db_and_tables():
    if init_engine():
        engine = init_engine()
        SQLModel.metadata.create_all(engine)
    else:
        return None

def insert_video_sub(video_id, zh_txt=None, en_txt=None, video_topic=None, playlist_id=None):
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
        
        engine = init_engine()
        if engine:
            with Session(engine) as session:
                new_sub = Subtitle(video_id=video_id, video_title=video_title, lang_code=language, channel_id=channel_id, channel_name=channel_name, zh_subtitle=zh_txt, en_subtitle=en_txt, playlist_id=playlist_id, content_topic=content_topic)
                session.add(new_sub)
                session.commit()
