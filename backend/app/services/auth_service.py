from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.schemas import UserCreate, TokenData
from app.core.config import settings
from app.constants.messages import ErrorMessages


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for authentication and authorization"""

    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(
        data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token"""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Optional[TokenData]:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            username: str = payload.get("sub")
            if username is None:
                return None
            return TokenData(username=username)
        except JWTError:
            return None

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create_user(
        self, user_data: UserCreate
    ) -> tuple[Optional[User], Optional[str]]:
        """Create a new user"""
        # Check username uniqueness
        existing_user = await self.get_user_by_username(user_data.username)
        if existing_user:
            return None, ErrorMessages.USERNAME_EXISTS

        # Check email uniqueness if provided
        if user_data.email:
            existing_email = await self.get_user_by_email(user_data.email)
            if existing_email:
                return None, ErrorMessages.EMAIL_EXISTS

        # Hash password
        password_hash = self.get_password_hash(user_data.password)

        # Create user
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=password_hash,
            system_user=user_data.system_user,
            is_active=1,
            is_admin=0,
        )

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        return new_user, None

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user by username and password"""
        user = await self.get_user_by_username(username)

        if not user:
            return None

        if not self.verify_password(password, user.password_hash):
            return None

        if not user.is_active:
            return None

        return user

    async def has_users(self) -> bool:
        """Check if any users exist in the database"""
        result = await self.db.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        return user is not None

    async def create_first_admin(
        self, user_data: UserCreate
    ) -> tuple[Optional[User], Optional[str]]:
        """Create first admin user (only works if no users exist)"""
        # Check if users already exist
        if await self.has_users():
            return None, ErrorMessages.SETUP_ALREADY_DONE

        # Create user with admin privileges
        user, error = await self.create_user(user_data)
        if error:
            return None, error

        # Make first user admin
        setattr(user, "is_admin", 1)
        await self.db.commit()
        await self.db.refresh(user)

        return user, None
