"""Authentication API endpoints."""
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from src.services.auth import AuthService, TokenData

router = APIRouter()

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)


class TokenResponse(BaseModel):
    """Token response."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


class UserRegisterRequest(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str
    full_name: str
    organization_id: Optional[str] = None


class UserResponse(BaseModel):
    """User response."""
    user_id: str
    email: str
    roles: list
    organization_id: Optional[str] = None


class PasswordChangeRequest(BaseModel):
    """Password change request."""
    current_password: str
    new_password: str


@router.post("/token", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login.
    
    Use username field for email.
    Returns access and refresh tokens.
    """
    auth_service = AuthService()
    
    # In production, this would:
    # 1. Look up user by email in database
    # 2. Verify password hash
    # 3. Check if user is active
    
    # Demo implementation - accepts any credentials
    # Replace with actual database lookup in production
    
    # Generate tokens
    access_token = auth_service.create_access_token(
        user_id="demo-user-001",
        email=form_data.username,
        roles=["user"],
    )
    
    refresh_token = auth_service.create_refresh_token(
        user_id="demo-user-001",
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=3600,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token.
    """
    auth_service = AuthService()
    
    result = auth_service.refresh_access_token(request.refresh_token)
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.error or "Invalid refresh token",
        )
    
    return TokenResponse(
        access_token=result.access_token,
        token_type=result.token_type,
        expires_in=result.expires_in,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)):
    """
    Get current authenticated user.
    
    Requires valid access token in Authorization header.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    auth_service = AuthService()
    result = auth_service.validate_token(token)
    
    if not result.valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.error or "Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return UserResponse(
        user_id=result.token_data.user_id,
        email=result.token_data.email,
        roles=result.token_data.roles,
        organization_id=result.token_data.organization_id,
    )


@router.post("/validate")
async def validate_token(token: Optional[str] = Depends(oauth2_scheme)):
    """
    Validate an access token.
    
    Returns token validity and decoded claims.
    """
    if not token:
        return {"valid": False, "error": "No token provided"}
    
    auth_service = AuthService()
    result = auth_service.validate_token(token)
    
    if result.valid:
        return {
            "valid": True,
            "user_id": result.token_data.user_id,
            "email": result.token_data.email,
            "roles": result.token_data.roles,
            "expires": result.token_data.exp.isoformat(),
        }
    else:
        return {"valid": False, "error": result.error}


@router.post("/register", response_model=UserResponse)
async def register_user(request: UserRegisterRequest):
    """
    Register a new user.
    
    Note: In production, this would:
    1. Check for existing email
    2. Hash password
    3. Create user in database
    4. Send verification email
    """
    auth_service = AuthService()
    
    # Hash password (for demo, not persisted)
    password_hash = auth_service.hash_password(request.password)
    
    # In production, save to database here
    # user = User(email=request.email, password_hash=password_hash, ...)
    # db.add(user)
    # await db.commit()
    
    # Demo response
    return UserResponse(
        user_id="new-user-001",
        email=request.email,
        roles=["user"],
        organization_id=request.organization_id,
    )


@router.post("/api-key")
async def generate_api_key(token: Optional[str] = Depends(oauth2_scheme)):
    """
    Generate an API key for programmatic access.
    
    Requires authentication. API key is tied to user's account.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    
    auth_service = AuthService()
    result = auth_service.validate_token(token)
    
    if not result.valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    # Generate API key
    api_key = auth_service.generate_api_key()
    
    # In production, save to database associated with user
    # api_key_record = APIKey(key=api_key, user_id=result.token_data.user_id)
    
    return {
        "api_key": api_key,
        "user_id": result.token_data.user_id,
        "note": "Store this key securely. It cannot be retrieved again.",
    }


@router.post("/logout")
async def logout(token: Optional[str] = Depends(oauth2_scheme)):
    """
    Logout / invalidate token.
    
    In production, this would add the token to a blacklist or revoke it.
    """
    if not token:
        return {"message": "No active session"}
    
    # In production: add token to blacklist
    # blacklist.add(token, expires=token.exp)
    
    return {"message": "Successfully logged out"}

