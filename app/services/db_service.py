from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional, List
import logging

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(String(20), default="user")  # user, verified_user, admin
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    is_banned = Column(Boolean, default=False)

class DownloadHistory(Base):
    __tablename__ = "download_history"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    url = Column(Text, nullable=False)
    platform = Column(String(50), nullable=False)
    status = Column(String(20), default="pending")  # pending, completed, failed
    file_path = Column(Text)
    file_size = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    error_message = Column(Text)

class DatabaseService:
    """SQLAlchemy-based database service for persistent data"""
    
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.logger = logging.getLogger(__name__)
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def get_or_create_user(self, user_id: int, username: str = None, 
                          first_name: str = None, last_name: str = None) -> User:
        """Get or create user"""
        with self.get_session() as session:
            user = session.query(User).filter(User.user_id == user_id).first()
            
            if not user:
                user = User(
                    user_id=user_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name
                )
                session.add(user)
                session.commit()
                session.refresh(user)
                self.logger.info(f"Created new user: {user_id}")
            else:
                # Update user info
                user.username = username
                user.first_name = first_name
                user.last_name = last_name
                user.last_seen = datetime.utcnow()
                session.commit()
            
            return user
    
    def update_user_role(self, user_id: int, role: str) -> bool:
        """Update user role"""
        with self.get_session() as session:
            user = session.query(User).filter(User.user_id == user_id).first()
            if user:
                user.role = role
                session.commit()
                return True
            return False
    
    def get_user_role(self, user_id: int) -> str:
        """Get user role"""
        with self.get_session() as session:
            user = session.query(User).filter(User.user_id == user_id).first()
            return user.role if user else "user"
    
    def ban_user(self, user_id: int, banned: bool = True) -> bool:
        """Ban or unban user"""
        with self.get_session() as session:
            user = session.query(User).filter(User.user_id == user_id).first()
            if user:
                user.is_banned = banned
                session.commit()
                return True
            return False
    
    def is_user_banned(self, user_id: int) -> bool:
        """Check if user is banned"""
        with self.get_session() as session:
            user = session.query(User).filter(User.user_id == user_id).first()
            return user.is_banned if user else False
    
    def create_download_record(self, user_id: int, url: str, platform: str) -> int:
        """Create download history record"""
        with self.get_session() as session:
            record = DownloadHistory(
                user_id=user_id,
                url=url,
                platform=platform
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return record.id
    
    def update_download_record(self, record_id: int, status: str, 
                             file_path: str = None, file_size: int = None, 
                             error_message: str = None):
        """Update download history record"""
        with self.get_session() as session:
            record = session.query(DownloadHistory).filter(DownloadHistory.id == record_id).first()
            if record:
                record.status = status
                if file_path:
                    record.file_path = file_path
                if file_size:
                    record.file_size = file_size
                if error_message:
                    record.error_message = error_message
                if status == "completed":
                    record.completed_at = datetime.utcnow()
                session.commit()