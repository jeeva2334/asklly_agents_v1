from db import Base
from sqlalchemy import Column, Integer, String, ARRAY, Boolean, TIMESTAMP, ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import date
from sqlalchemy.dialects.postgresql import JSONB

class CreatingBot(Base):
    __tablename__ = 'created_bots'

    id = Column(Integer, primary_key=True)
    botname = Column(String(255))
    training_files = Column(String(255))
    apikey = Column(String(255))
    uid = Column(String(255))
    image = Column(String(255))
    color = Column(String(255))
    textcolor = Column(String(255))
    title = Column(String(255))
    initial = Column(String(255))
    created_at = Column(String(255))
    organization = Column(String(255))
    chats = Column(Integer, default=0)
    views = Column(Integer, default=0)
    tags = Column(ARRAY(String))
    team_id = Column(Integer)
    prompt = Column(String)
    default_websearch = Column(Boolean, default=False)
    model = Column(String, default="DeepSeek R1 Distill Llama 70B")

class LLMModels(Base):
    __tablename__ = 'models'

    id = Column(Integer, primary_key=True)
    model_id = Column(String)
    model_name = Column(String)

class KnowledgeBase(Base):
    __tablename__ = 'knowledge_base'

    id = Column(Integer, primary_key=True)
    kb_name = Column(String(255))
    file_name = Column(String(255))
    created_by = Column(String(255))
    last_modified = Column(String(255))
    location = Column(String(255))
    organization = Column(String(255))
    file_type = Column(String(255))
    file_size = Column(String(255))
    created_id = Column(String(255))
    status = Column(String(255))
    kb_id = Column(String(255))

class KBIndexIDs(Base):
    __tablename__ = 'kbindexids'

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String(255), nullable=True)
    table_name = Column(String(255), nullable=True)
    index_ids = Column(JSONB, nullable=True)  # store list of IDs as JSON array
    organization = Column(String(255), nullable=True)

class TokenMetrics(Base):
    __tablename__ = 'token_metrics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization = Column(String(255), nullable=False)
    usage_type = Column(String(50), nullable=False)  # 'chat' or 'knowledge_base'
    bot_key = Column(String(255), nullable=False)    # ✅ New field
    chat_tokens = Column(Integer, default=0)
    embed_tokens = Column(Integer, default=0)
    usage_date = Column(Date, default=date.today, nullable=False)
    api_calls = Column(Integer, default=0)

    __table_args__ = (
        UniqueConstraint('organization', 'usage_type', 'bot_key', 'usage_date', name='unique_usage_per_day_per_bot'),
    )

class KbIndex(Base):
    __tablename__ = 'kb_index'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)  # Ensure auto-generated primary key values
    file_name = Column(String, nullable=False)  # Added nullable=False for better integrity
    table_name = Column(String, nullable=False)  # Added nullable=False for better integrity
    consolidated_index_ids = Column(ARRAY(String), nullable=True)  # Allowing NULL values for this field
    organization = Column(String, nullable=False)  # Added nullable=False for better integrity

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    isverified = Column(Boolean)
    uname = Column(String)
    prof = Column(String)
    onboarded = Column(Boolean)

class Team(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_name = Column(String(255))
    team_contact_email = Column(String(255))
    owner = Column(String(255))
    email_addresses = Column(String(255))
    secure_signin = Column(Boolean)
    knowledge_base_limit = Column(String(255))
    organization = Column(String(255))
    created_at = Column(TIMESTAMP, nullable=False, server_default='CURRENT_TIMESTAMP')
    status = Column(Boolean)

    # Define a one-to-many relationship between teams and members
    members = relationship('Member', back_populates='team')

class Member(Base):
    __tablename__ = 'members'

    id = Column(Integer, primary_key=True, autoincrement=True)
    member_name = Column(String(255))
    role = Column(String(100))
    status = Column(String(100))
    signin_method = Column(String(100))
    organization = Column(String(255))
    created_at = Column(TIMESTAMP, nullable=False, server_default='CURRENT_TIMESTAMP')
    team_id = Column(Integer, ForeignKey('teams.id'))
    status = Column(String(255))

    # Define a many-to-one relationship between members and teams
    team = relationship('Team', back_populates='members')