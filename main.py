from fastapi import FastAPI, BackgroundTasks
from sqlmodel import Session, select


from db_helper import init_engine, insert_video_sub
from model import Subtitle
from util import get_subtitle

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


# Get subtitle by video ID and lang_code (default 'zh')
@app.get("/subtitle/{video_id}")
async def get_video_sub(video_id: str, background_tasks: BackgroundTasks, user_prompt: str | None = None, lang_code: str | None = 'zh', video_content: str | None = None, playlist_id: str |None = None):
    # create sqlmodel engine for db connection
    engine = init_engine()
    if engine:
        with Session(engine) as session:
            statement = select(Subtitle).where(Subtitle.video_id == video_id)
            result = session.exec(statement).first()
            if result:
                if lang_code == 'zh':
                    return {"result": result.zh_subtitle}
                else:
                    return {"result": result.en_subtitle}
            # if requested video subtitle not found in db
            else:
                # Call cloud function to fetch subtitle
                sub = get_subtitle(video_id, user_prompt)

                # Background task: add video to database 
                if lang_code == 'zh':
                    background_tasks.add_task(insert_video_sub, video_id, zh_txt=sub, video_topic=video_content, playlist_id=playlist_id)
                else:
                    background_tasks.add_task(insert_video_sub, video_id, en_txt=sub, video_topic=video_content, playlist_id=playlist_id)

                return {"result": sub}
         
    else:
        print("Engine not created!")
        return {"result": "Engine not created!"}


# Get all subtitles by channel ID or playlist ID, lang_code (default 'zh')
@app.get("/subtitles")
def all_subs(channel_id: str | None = None, playlist_id: str | None = None, lang_code: str | None = 'zh'):
    engine = init_engine()
    if engine:
        with Session(engine) as session:
            if channel_id:
                selete_channel = select(Subtitle).where(Subtitle.channel_id == channel_id)
                channel_videos = session.exec(selete_channel).all()
                return {"result": channel_videos}
            if playlist_id:
                select_playlist = select(Subtitle).where(Subtitle.playlist_id == playlist_id)
                playlist_videos = session.exec(select_playlist).all()
                return {"result": playlist_videos}
            
            select_all = select(Subtitle)
            all_videos = session.exec(select_all).all()
            return {"result": all_videos}

    else:
        print("Engine not created!")
        return {"result": "Engine not created!"}

