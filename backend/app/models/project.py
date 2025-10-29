from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True, nullable=False, index=True)
    slug = Column(
        String(255), unique=True, nullable=False, index=True
    )  # URL-safe identifier from domain
    port = Column(Integer, nullable=True)  # Deprecated, kept for compatibility
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    compose_content = Column(Text, nullable=False)
    env_vars = Column(Text, nullable=True, default="{}")  # JSON string
    # created, running, stopped, error
    status = Column(String(50), default="created")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships (using string to avoid circular import)
    owner = relationship("User", back_populates="projects", lazy="joined")
