from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.sql import func
from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True, nullable=False, index=True)
    port = Column(Integer, nullable=True)
    compose_content = Column(Text, nullable=False)
    env_vars = Column(Text, nullable=True, default="{}")  # JSON string
    status = Column(String(50), default="created")  # created, running, stopped, error
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('ix_projects_domain', 'domain', unique=True),
    )

