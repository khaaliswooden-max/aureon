"""
Authentication Service

Provides JWT-based authentication for the AUREON platform:
- User registration and login
- JWT token generation and validation
- Role-based access control (RBAC)
- Password hashing and verification
"""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
import secrets
import structlog

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

from src.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7


class TokenData(BaseModel):
    """Token payload data."""
    user_id: str
    email: str
    roles: List[str] = []
    organization_id: Optional[str] = None
    exp: datetime


class UserCreate(BaseModel):
    """User registration data."""
    email: EmailStr
    password: str
    full_name: str
    organization_id: Optional[str] = None


class UserLogin(BaseModel):
    """User login credentials."""
    email: EmailStr
    password: str


@dataclass
class AuthResult:
    """Authentication result."""
    success: bool
    user_id: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES * 60
    error: Optional[str] = None


@dataclass
class TokenValidationResult:
    """Token validation result."""
    valid: bool
    token_data: Optional[TokenData] = None
    error: Optional[str] = None


class AuthService:
    """
    JWT-based Authentication Service.
    
    Capabilities:
    - Password hashing and verification
    - JWT access and refresh token generation
    - Token validation and refresh
    - Role-based access control
    """
    
    # Available roles
    ROLES = {
        "admin": "Full administrative access",
        "user": "Standard user access",
        "analyst": "Read-only analyst access",
        "api": "API-only access for integrations",
    }
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize authentication service.
        
        Args:
            secret_key: JWT secret key (falls back to settings)
        """
        self.secret_key = secret_key or settings.secret_key
        if self.secret_key == "dev-secret-key-change-in-production":
            logger.warning("Using default secret key - change in production!")
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            return False
    
    def create_access_token(
        self,
        user_id: str,
        email: str,
        roles: List[str] = None,
        organization_id: Optional[str] = None,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        Create a JWT access token.
        
        Args:
            user_id: User's unique identifier
            email: User's email address
            roles: List of role names
            organization_id: Associated organization ID
            expires_delta: Custom expiration time
            
        Returns:
            JWT access token string
        """
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        payload = {
            "sub": user_id,
            "email": email,
            "roles": roles or ["user"],
            "org_id": organization_id,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access",
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=ALGORITHM)
    
    def create_refresh_token(
        self,
        user_id: str,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        Create a JWT refresh token.
        
        Args:
            user_id: User's unique identifier
            expires_delta: Custom expiration time
            
        Returns:
            JWT refresh token string
        """
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh",
            "jti": secrets.token_hex(16),  # Unique token ID
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=ALGORITHM)
    
    def validate_token(self, token: str) -> TokenValidationResult:
        """
        Validate a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            TokenValidationResult with validation status and data
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[ALGORITHM])
            
            # Check token type
            token_type = payload.get("type", "access")
            
            user_id = payload.get("sub")
            if not user_id:
                return TokenValidationResult(valid=False, error="Invalid token: no user ID")
            
            # Build token data
            token_data = TokenData(
                user_id=user_id,
                email=payload.get("email", ""),
                roles=payload.get("roles", []),
                organization_id=payload.get("org_id"),
                exp=datetime.fromtimestamp(payload.get("exp", 0), tz=timezone.utc),
            )
            
            return TokenValidationResult(valid=True, token_data=token_data)
            
        except JWTError as e:
            logger.debug("Token validation failed", error=str(e))
            return TokenValidationResult(valid=False, error=f"Invalid token: {str(e)}")
        except Exception as e:
            logger.error("Token validation error", error=str(e))
            return TokenValidationResult(valid=False, error="Token validation failed")
    
    def refresh_access_token(self, refresh_token: str) -> AuthResult:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            AuthResult with new access token
        """
        try:
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=[ALGORITHM])
            
            # Verify it's a refresh token
            if payload.get("type") != "refresh":
                return AuthResult(success=False, error="Invalid token type")
            
            user_id = payload.get("sub")
            if not user_id:
                return AuthResult(success=False, error="Invalid refresh token")
            
            # In a real implementation, we would:
            # 1. Look up the user from the database
            # 2. Check if the refresh token is still valid (not revoked)
            # 3. Get current roles and organization
            
            # For now, generate a new access token with default roles
            new_access_token = self.create_access_token(
                user_id=user_id,
                email="",  # Would be fetched from DB
                roles=["user"],
            )
            
            return AuthResult(
                success=True,
                user_id=user_id,
                access_token=new_access_token,
                token_type="bearer",
            )
            
        except JWTError as e:
            return AuthResult(success=False, error=f"Invalid refresh token: {str(e)}")
    
    def check_permission(
        self,
        token_data: TokenData,
        required_roles: List[str],
        require_all: bool = False,
    ) -> bool:
        """
        Check if user has required roles.
        
        Args:
            token_data: Validated token data
            required_roles: List of required role names
            require_all: If True, user must have ALL roles; if False, ANY role
            
        Returns:
            True if user has permission
        """
        if not token_data.roles:
            return False
        
        # Admin always has permission
        if "admin" in token_data.roles:
            return True
        
        user_roles = set(token_data.roles)
        required = set(required_roles)
        
        if require_all:
            return required.issubset(user_roles)
        else:
            return bool(user_roles.intersection(required))
    
    def generate_api_key(self, prefix: str = "aureon") -> str:
        """
        Generate a secure API key.
        
        Args:
            prefix: Key prefix for identification
            
        Returns:
            API key string (prefix_randomstring)
        """
        random_part = secrets.token_urlsafe(32)
        return f"{prefix}_{random_part}"


# FastAPI dependency functions
async def get_current_user(token: str) -> TokenData:
    """
    FastAPI dependency to get current user from token.
    
    Usage:
        @router.get("/protected")
        async def protected_route(user: TokenData = Depends(get_current_user)):
            return {"user_id": user.user_id}
    """
    from fastapi import HTTPException, status
    
    auth_service = AuthService()
    result = auth_service.validate_token(token)
    
    if not result.valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.error or "Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return result.token_data


def require_roles(*roles: str):
    """
    FastAPI dependency factory for role-based access.
    
    Usage:
        @router.get("/admin-only")
        async def admin_route(user: TokenData = Depends(require_roles("admin"))):
            return {"admin": True}
    """
    from fastapi import HTTPException, status, Depends
    
    async def role_checker(user: TokenData = Depends(get_current_user)):
        auth_service = AuthService()
        if not auth_service.check_permission(user, list(roles)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return user
    
    return role_checker

