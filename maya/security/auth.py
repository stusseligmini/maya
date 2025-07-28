"""Security utilities for Maya system."""

try:
    from jose import jwt, JWTError
    JWT_AVAILABLE = True
except ImportError:
    try:
        import jwt
        from jwt import PyJWTError as JWTError
        JWT_AVAILABLE = True
    except ImportError:
        JWT_AVAILABLE = False

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

try:
    from passlib.context import CryptContext
    PASSLIB_AVAILABLE = True
except ImportError:
    PASSLIB_AVAILABLE = False

try:
    from fastapi import HTTPException, Depends, status
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

import secrets
import re
from dataclasses import dataclass

from maya.core.exceptions import AuthenticationError, ValidationError
from maya.core.logging import LoggerMixin
from maya.config.settings import get_settings


@dataclass
class TokenData:
    """Token data structure."""
    user_id: str
    username: str
    email: str
    scopes: List[str]
    exp: datetime


class PasswordValidator(LoggerMixin):
    """Password validation utilities."""
    
    MIN_LENGTH = 8
    
    def validate_password(self, password: str) -> List[str]:
        """Validate password strength."""
        issues = []
        
        if len(password) < self.MIN_LENGTH:
            issues.append(f"Password must be at least {self.MIN_LENGTH} characters long")
        
        if not re.search(r"[A-Z]", password):
            issues.append("Password must contain at least one uppercase letter")
        
        if not re.search(r"[a-z]", password):
            issues.append("Password must contain at least one lowercase letter")
        
        if not re.search(r"\d", password):
            issues.append("Password must contain at least one digit")
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            issues.append("Password must contain at least one special character")
        
        # Check for common patterns
        common_patterns = [
            r"123456", r"password", r"qwerty", r"abc123", 
            r"admin", r"letmein", r"welcome"
        ]
        
        for pattern in common_patterns:
            if re.search(pattern, password.lower()):
                issues.append("Password contains common patterns and is not secure")
                break
        
        if issues:
            self.logger.warning("Password validation failed", issues_count=len(issues))
        else:
            self.logger.info("Password validation passed")
        
        return issues


class InputValidator(LoggerMixin):
    """Input validation utilities."""
    
    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_valid = re.match(pattern, email) is not None
        
        if not is_valid:
            self.logger.warning("Invalid email format", email=email)
        
        return is_valid
    
    def validate_username(self, username: str) -> List[str]:
        """Validate username."""
        issues = []
        
        if len(username) < 3:
            issues.append("Username must be at least 3 characters long")
        
        if len(username) > 30:
            issues.append("Username must be no more than 30 characters long")
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            issues.append("Username can only contain letters, numbers, hyphens, and underscores")
        
        if username.startswith('-') or username.endswith('-'):
            issues.append("Username cannot start or end with a hyphen")
        
        return issues
    
    def sanitize_input(self, text: str, max_length: int = 1000) -> str:
        """Sanitize text input."""
        if not text:
            return ""
        
        # Remove potential XSS patterns
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
        
        # Limit length
        if len(text) > max_length:
            text = text[:max_length]
            self.logger.warning("Input truncated due to length", 
                              original_length=len(text), max_length=max_length)
        
        return text.strip()


class PasswordManager(LoggerMixin):
    """Password hashing and verification."""
    
    def __init__(self):
        if not PASSLIB_AVAILABLE:
            self.logger.warning("passlib not available, using basic password handling")
            self.pwd_context = None
        else:
            self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        self.validator = PasswordValidator()
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        # Validate password strength first
        issues = self.validator.validate_password(password)
        if issues:
            raise ValidationError(f"Password validation failed: {', '.join(issues)}")
        
        if self.pwd_context:
            hashed = self.pwd_context.hash(password)
            self.logger.info("Password hashed successfully")
            return hashed
        else:
            # Fallback to basic hashing (not secure for production)
            import hashlib
            hashed = hashlib.sha256(password.encode()).hexdigest()
            self.logger.warning("Using fallback password hashing - not secure for production")
            return hashed
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        try:
            if self.pwd_context:
                is_valid = self.pwd_context.verify(plain_password, hashed_password)
                if is_valid:
                    self.logger.info("Password verification successful")
                else:
                    self.logger.warning("Password verification failed")
                return is_valid
            else:
                # Fallback verification (not secure for production)
                import hashlib
                expected_hash = hashlib.sha256(plain_password.encode()).hexdigest()
                is_valid = expected_hash == hashed_password
                if is_valid:
                    self.logger.info("Password verification successful (fallback)")
                else:
                    self.logger.warning("Password verification failed (fallback)")
                return is_valid
        except Exception as e:
            self.logger.error("Password verification error", error=str(e))
            return False
    
    def generate_secure_password(self, length: int = 16) -> str:
        """Generate a secure random password."""
        if length < 8:
            length = 8
        
        # Include different character types
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        password = ''.join(secrets.choice(chars) for _ in range(length))
        
        # Ensure it meets requirements
        issues = self.validator.validate_password(password)
        if issues:
            # Regenerate if it doesn't meet requirements (rare but possible)
            return self.generate_secure_password(length)
        
        return password


class JWTManager(LoggerMixin):
    """JWT token management."""
    
    def __init__(self):
        self.settings = get_settings()
        # Use flattened settings structure
        self.secret_key = self.settings.SECRET_KEY
        self.algorithm = self.settings.ALGORITHM
        self.access_token_expire_minutes = self.settings.ACCESS_TOKEN_EXPIRE_MINUTES
        
        if not JWT_AVAILABLE:
            self.logger.warning("JWT library not available, using fallback token handling")
    
    def create_access_token(
        self, 
        user_id: str, 
        username: str, 
        email: str,
        scopes: Optional[List[str]] = None
    ) -> str:
        """Create a JWT access token."""
        if scopes is None:
            scopes = ["read"]
        
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            "sub": user_id,
            "username": username,
            "email": email,
            "scopes": scopes,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        try:
            if JWT_AVAILABLE:
                token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
                self.logger.info("Access token created", user_id=user_id, expires=expire.isoformat())
                return token
            else:
                # Fallback: create a simple base64 encoded token (NOT secure for production)
                import base64
                import json
                token_data = json.dumps(payload, default=str)
                token = base64.b64encode(token_data.encode()).decode()
                self.logger.warning("Using fallback token creation - not secure for production")
                return token
        except Exception as e:
            self.logger.error("Token creation failed", error=str(e))
            raise AuthenticationError(f"Token creation failed: {str(e)}")
    
    def verify_token(self, token: str) -> TokenData:
        """Verify and decode a JWT token."""
        try:
            if JWT_AVAILABLE:
                payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            else:
                # Fallback: decode base64 token (NOT secure for production)
                import base64
                import json
                token_data = base64.b64decode(token.encode()).decode()
                payload = json.loads(token_data)
                self.logger.warning("Using fallback token verification - not secure for production")
            
            user_id = payload.get("sub")
            username = payload.get("username")
            email = payload.get("email")
            scopes = payload.get("scopes", [])
            exp_timestamp = payload.get("exp")
            
            # Handle different datetime formats
            if isinstance(exp_timestamp, str):
                from datetime import datetime as dt
                exp = dt.fromisoformat(exp_timestamp.replace('Z', '+00:00'))
            else:
                from datetime import datetime as dt
                exp = dt.fromtimestamp(exp_timestamp)
            
            if not user_id or not username or not email:
                raise AuthenticationError("Invalid token payload")
            
            token_data = TokenData(
                user_id=user_id,
                username=username,
                email=email,
                scopes=scopes,
                exp=exp
            )
            
            self.logger.info("Token verified successfully", user_id=user_id)
            return token_data
            
        except Exception as e:
            if 'expired' in str(e).lower():
                self.logger.warning("Token has expired")
                raise AuthenticationError("Token has expired")
            else:
                self.logger.warning("Token verification failed", error=str(e))
                raise AuthenticationError("Could not validate token")
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create a refresh token."""
        expire = datetime.utcnow() + timedelta(days=30)  # Longer expiry for refresh tokens
        
        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        try:
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            self.logger.info("Refresh token created", user_id=user_id)
            return token
        except Exception as e:
            self.logger.error("Refresh token creation failed", error=str(e))
            raise AuthenticationError(f"Refresh token creation failed: {str(e)}")


class APIKeyManager(LoggerMixin):
    """API key management for external access."""
    
    def generate_api_key(self, prefix: str = "maya") -> str:
        """Generate a secure API key."""
        random_part = secrets.token_urlsafe(32)
        api_key = f"{prefix}_{random_part}"
        
        self.logger.info("API key generated", prefix=prefix)
        return api_key
    
    def validate_api_key_format(self, api_key: str) -> bool:
        """Validate API key format."""
        pattern = r'^[a-zA-Z0-9_]+_[A-Za-z0-9_-]{32,}$'
        is_valid = re.match(pattern, api_key) is not None
        
        if not is_valid:
            self.logger.warning("Invalid API key format")
        
        return is_valid


class SecurityHeaders:
    """Security headers for HTTP responses."""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get recommended security headers."""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }


class RateLimiter(LoggerMixin):
    """Simple rate limiting implementation."""
    
    def __init__(self):
        self.requests = {}
    
    def is_allowed(
        self, 
        identifier: str, 
        max_requests: int = 100, 
        window_minutes: int = 60
    ) -> bool:
        """Check if request is allowed based on rate limit."""
        current_time = datetime.utcnow()
        window_start = current_time - timedelta(minutes=window_minutes)
        
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Remove old requests outside the window
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier] 
            if req_time > window_start
        ]
        
        # Check if limit exceeded
        if len(self.requests[identifier]) >= max_requests:
            self.logger.warning("Rate limit exceeded", 
                              identifier=identifier, 
                              requests_count=len(self.requests[identifier]))
            return False
        
        # Add current request
        self.requests[identifier].append(current_time)
        return True


# Security dependency for FastAPI
if FASTAPI_AVAILABLE:
    security = HTTPBearer()
else:
    security = None

jwt_manager = JWTManager()
password_manager = PasswordManager()
input_validator = InputValidator()
api_key_manager = APIKeyManager()
rate_limiter = RateLimiter()


if FASTAPI_AVAILABLE:
    async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
        """FastAPI dependency to get current authenticated user."""
        try:
            token_data = jwt_manager.verify_token(credentials.credentials)
            return token_data
        except AuthenticationError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )


    async def require_scopes(required_scopes: List[str]):
        """FastAPI dependency to require specific scopes."""
        def scope_checker(current_user: TokenData = Depends(get_current_user)) -> TokenData:
            for scope in required_scopes:
                if scope not in current_user.scopes:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Not enough permissions. Required scope: {scope}"
                    )
            return current_user
        
        return scope_checker

else:
    # Fallback functions when FastAPI is not available
    def get_current_user(*args, **kwargs):
        """Fallback function when FastAPI is not available."""
        raise NotImplementedError("FastAPI not available - cannot use authentication dependencies")
    
    def require_scopes(required_scopes: List[str]):
        """Fallback function when FastAPI is not available."""
        def scope_checker(*args, **kwargs):
            raise NotImplementedError("FastAPI not available - cannot use scope checking")
        return scope_checker