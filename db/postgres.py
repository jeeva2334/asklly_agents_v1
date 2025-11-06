from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import logging
import config

log = logging.getLogger(__name__)

DATABASE_URL = config.POSTGRES_URL
engine = create_engine(
    DATABASE_URL,
    pool_recycle=300,
    pool_pre_ping=True,
    poolclass=NullPool
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()