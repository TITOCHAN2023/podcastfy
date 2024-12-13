from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from logger import logger

from .models import BaseSchema
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


@logger.catch
def init_mysql_session() -> sessionmaker[Session]:

    engine = create_engine(
        DATABASE_URL,
        connect_args={
            "charset": "utf8mb4",
        },
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_use_lifo=True,
        pool_recycle=3600,
    )

    session = sessionmaker(bind=engine)

    BaseSchema.metadata.create_all(engine)
    logger.info("Init session successfully")

    return session


session = init_mysql_session()
