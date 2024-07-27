from fastapi import Depends, FastAPI, BackgroundTasks
from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from db_helper import get_db, insert_video_sub
from model import Subtitle
from util import get_subtitle

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "This is video subtitle fastapi."}

# Get subtitle by video ID and lang_code (default 'zh')
# Call cloud function to get subtitle if video not found in database, then save video subtitles to database in background task
@app.get("/subtitle/{video_id}")
async def get_video_sub(video_id: str, background_tasks: BackgroundTasks, user_prompt: str | None = None, lang_code: str | None = 'zh', video_content: str | None = None, playlist_id: str |None = None, session: AsyncSession = Depends(get_db)):
    result = await session.exec(select(Subtitle).where(Subtitle.video_id == video_id))
    video = result.scalar_one_or_none()
    if video:
        if lang_code == 'zh':
            return {"result": video.zh_subtitle}
        else:
            return {"result": video.en_subtitle}
    # if requested video subtitle not found in db
    else:
        # Call cloud function to fetch subtitle
        sub = get_subtitle(video_id, user_prompt)

        # Background task: add video to database 
        if lang_code == 'zh':
            background_tasks.add_task(insert_video_sub, session, video_id, zh_txt=sub, video_topic=video_content, playlist_id=playlist_id, )
        else:
            background_tasks.add_task(insert_video_sub, session, video_id, en_txt=sub, video_topic=video_content, playlist_id=playlist_id)

        return {"result": sub}

# Get all subtitles by channel ID or playlist ID, lang_code (default 'zh')
@app.get("/subtitles")
async def all_subs(channel_id: str | None = None, playlist_id: str | None = None, lang_code: str | None = 'zh', session: AsyncSession = Depends(get_db)):
    if channel_id:
        selete_channel = select(Subtitle).where(Subtitle.channel_id == channel_id)
        channel_videos = await session.exec(selete_channel)
        result = channel_videos.scalars().all()
    if playlist_id:
        select_playlist = select(Subtitle).where(Subtitle.playlist_id == playlist_id)
        playlist_videos = await session.exec(select_playlist)
        result = playlist_videos.scalars().all()
    return {"results": result}
