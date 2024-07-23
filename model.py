from sqlmodel import Field, SQLModel
from sqlalchemy import Column, DateTime, func
from typing import Optional
from datetime import datetime


class Subtitle(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    video_id: str = Field(unique=True, nullable=False, max_length=100)
    video_title: str = Field(nullable=False, max_length=255)
    content_topic: str = Field(default='Car', max_length=100)
    lang_code: str = Field(nullable=False, max_length=5)
    en_subtitle: str | None = None
    zh_subtitle: str | None = None
    channel_id: str | None = Field(max_length=100, default=None)
    playlist_id: str | None = Field(max_length=100, default=None)
    created_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(), server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(), onupdate=func.now())
    )
    channel_name: str | None = Field(max_length=100, default=None)
