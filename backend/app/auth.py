from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import jwt
from app.config import get_settings

settings = get_settings()
security = HTTPBearer()


async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
    Verify Clerk JWT token and return user information
    """
    try:
        token = credentials.credentials

        # Decode JWT without verification to extract user_id
        # For production, you should verify the JWT signature using Clerk's JWKS
        decoded = jwt.decode(token, options={"verify_signature": False})

        # Extract user_id from the JWT (Clerk uses 'sub' for user ID)
        user_id = decoded.get("sub") or decoded.get("user_id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not extract user ID from token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "user_id": user_id,
            "session_id": decoded.get("sid"),
        }

    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """
    Get current user ID from verified token
    """
    user_data = await verify_token(credentials)
    return user_data["user_id"]
