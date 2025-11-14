"""
FastAPI Test Server for Auth Matrix Integration Testing

This server provides a simple API with different authentication levels
to test the Auth Matrix application's authorization testing capabilities.

Authentication:
- Public endpoints: No authentication required
- User endpoints: Require bearer token "user_token_123"
- Admin endpoints: Require bearer token "admin_token_456"
"""

from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Auth Matrix Test API",
    description="Test API server for validating authorization matrices",
    version="1.0.0"
)

# Security scheme
security = HTTPBearer(auto_error=False)

# Valid tokens for testing
VALID_TOKENS: Dict[str, str] = {
    "user_token_123": "user",
    "admin_token_456": "admin"
}


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    message: str


class PublicResponse(BaseModel):
    """Public endpoint response model"""
    message: str
    access_level: str


class UserResponse(BaseModel):
    """User endpoint response model"""
    message: str
    user_id: str
    access_level: str


class AdminResponse(BaseModel):
    """Admin endpoint response model"""
    message: str
    admin_data: Dict[str, Any]
    access_level: str


def get_current_user_role(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Optional[str]:
    """
    Validate bearer token and return user role.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        User role ('user', 'admin') or None for guest
        
    Raises:
        HTTPException: If token is invalid
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    role = VALID_TOKENS.get(token)
    
    if role is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )
    
    return role


def require_authentication(role: Optional[str] = Depends(get_current_user_role)) -> str:
    """
    Require any valid authentication.
    
    Args:
        role: User role from token validation
        
    Returns:
        User role
        
    Raises:
        HTTPException: If not authenticated
    """
    if role is None:
        raise HTTPException(
            status_code=403,
            detail="Authentication required"
        )
    return role


def require_admin(role: str = Depends(require_authentication)) -> str:
    """
    Require admin role.
    
    Args:
        role: User role from authentication
        
    Returns:
        Admin role
        
    Raises:
        HTTPException: If not admin
    """
    if role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required"
        )
    return role


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check() -> HealthResponse:
    """
    Health check endpoint - always accessible.
    
    Returns:
        Health status
    """
    logger.info("Health check requested")
    return HealthResponse(
        status="healthy",
        message="API is running"
    )


@app.get("/public", response_model=PublicResponse, tags=["Public"])
async def public_endpoint() -> PublicResponse:
    """
    Public endpoint - no authentication required.
    
    Returns:
        Public information
    """
    logger.info("Public endpoint accessed")
    return PublicResponse(
        message="This is a public endpoint",
        access_level="public"
    )


@app.get("/user/profile", response_model=UserResponse, tags=["User"])
async def user_profile(role: str = Depends(require_authentication)) -> UserResponse:
    """
    User profile endpoint - requires authentication (user or admin).
    
    Args:
        role: Authenticated user role
        
    Returns:
        User profile information
    """
    logger.info(f"User profile accessed by: {role}")
    return UserResponse(
        message="User profile retrieved",
        user_id=f"{role}_id_001",
        access_level=role
    )


@app.get("/user/data", response_model=UserResponse, tags=["User"])
async def user_data(role: str = Depends(require_authentication)) -> UserResponse:
    """
    User data endpoint - requires authentication (user or admin).
    
    Args:
        role: Authenticated user role
        
    Returns:
        User data
    """
    logger.info(f"User data accessed by: {role}")
    return UserResponse(
        message="User data retrieved",
        user_id=f"{role}_id_001",
        access_level=role
    )


@app.get("/admin/dashboard", response_model=AdminResponse, tags=["Admin"])
async def admin_dashboard(role: str = Depends(require_admin)) -> AdminResponse:
    """
    Admin dashboard endpoint - requires admin authentication.
    
    Args:
        role: Admin role from authentication
        
    Returns:
        Admin dashboard data
    """
    logger.info("Admin dashboard accessed")
    return AdminResponse(
        message="Admin dashboard accessed",
        admin_data={
            "total_users": 42,
            "active_sessions": 15,
            "system_status": "operational"
        },
        access_level="admin"
    )


@app.get("/admin/users", response_model=AdminResponse, tags=["Admin"])
async def admin_users(role: str = Depends(require_admin)) -> AdminResponse:
    """
    Admin users endpoint - requires admin authentication.
    
    Args:
        role: Admin role from authentication
        
    Returns:
        User management data
    """
    logger.info("Admin users endpoint accessed")
    return AdminResponse(
        message="User list retrieved",
        admin_data={
            "users": [
                {"id": 1, "name": "Alice", "role": "user"},
                {"id": 2, "name": "Bob", "role": "user"},
                {"id": 3, "name": "Charlie", "role": "admin"}
            ]
        },
        access_level="admin"
    )


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
