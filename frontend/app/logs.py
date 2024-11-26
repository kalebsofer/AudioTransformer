import psycopg2
from config.settings import get_settings
import uuid
import streamlit as st
from dataclasses import dataclass, field
from datetime import datetime, timezone

settings = get_settings()


@dataclass
class CaptionLog:
    user_id: str
    session_id: str
    image_id: str
    generated_caption: str
    rating: int
    ideal_caption: str
    feedback_received: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class LogManager:
    def __init__(self):
        self.settings = get_settings()

    def get_db_connection(self):
        return psycopg2.connect(
            dbname=self.settings.POSTGRES_DB,
            user=self.settings.POSTGRES_USER,
            password=self.settings.POSTGRES_PASSWORD,
            host="postgres",
            port="5432",
        )

    @staticmethod
    def get_or_create_user_id():
        if "user_id" not in st.session_state:
            st.session_state.user_id = str(uuid.uuid4())
        return st.session_state.user_id

    @staticmethod
    def get_or_create_session_id():
        if "session_id" not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        return st.session_state.session_id

    def log_caption(
        self,
        image_id: str,
        generated_caption: str,
        feedback_received: bool,
        rating: int,
        ideal_caption: str,
    ):
        log = CaptionLog(
            user_id=self.get_or_create_user_id(),
            session_id=self.get_or_create_session_id(),
            image_id=image_id,
            generated_caption=generated_caption,
            feedback_received=feedback_received,
            rating=rating,
            ideal_caption=ideal_caption,
            created_at=datetime.now(timezone.utc),
        )

        with self.get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO caption_logs 
                    (user_id, session_id, image_id, generated_caption, feedback_received, rating, ideal_caption, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s AT TIME ZONE 'UTC')
                    """,
                    (
                        log.user_id,
                        log.session_id,
                        log.image_id,
                        log.generated_caption,
                        log.feedback_received,
                        log.rating,
                        log.ideal_caption,
                        log.created_at,
                    ),
                )
            conn.commit()

    def update_feedback(self, query: str, selected_document: str):
        user_id = self.get_or_create_user_id()
        session_id = self.get_or_create_session_id()

        with self.get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE caption_logs 
                    SET feedback_received = TRUE 
                    WHERE user_id = %s
                    AND session_id = %s
                    AND image_id = %s 
                    AND generated_caption = %s 
                    AND created_at = (
                        SELECT created_at 
                        FROM caption_logs 
                        WHERE user_id = %s 
                        AND session_id = %s 
                        AND image_id = %s 
                        AND generated_caption = %s 
                        ORDER BY created_at DESC 
                        LIMIT 1
                    )
                    """,
                    (
                        user_id,
                        session_id,
                        query,
                        selected_document,
                        user_id,
                        session_id,
                        query,
                        selected_document,
                    ),
                )
            conn.commit()


log_manager = LogManager()