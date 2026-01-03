"""
Authentication module for Diet Coach API
Handles user registration, login, JWT token management, and password security
"""

import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# JWT handling
import base64
import hmac

logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "diet-coach-super-secret-key-change-in-production-2024")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))
USERS_FILE = Path(os.getenv("USERS_FILE", "/app/users.json"))

# Fallback paths for users file
USERS_PATHS = [
    Path("/app/users.json"),
    Path("users.json"),
    Path("./users.json"),
]


class AuthError(Exception):
    """Custom authentication error"""
    pass


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


@dataclass
class User:
    """User data model"""
    id: str
    email: str
    password_hash: str
    name: str
    created_at: str
    updated_at: str
    is_active: bool = True
    profile: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_public_dict(self) -> Dict[str, Any]:
        """Return user data without sensitive information"""
        data = self.to_dict()
        del data['password_hash']
        return data


@dataclass
class TokenPayload:
    """JWT token payload"""
    user_id: str
    email: str
    token_type: str
    exp: float
    iat: float


class PasswordHasher:
    """Secure password hashing using PBKDF2"""
    
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> str:
        """Hash password with salt using PBKDF2"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 with SHA256
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        ).hex()
        
        # Return salt:hash format
        return f"{salt}:{password_hash}"
    
    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        try:
            salt, _ = stored_hash.split(':')
            return PasswordHasher.hash_password(password, salt) == stored_hash
        except ValueError:
            return False


class JWTManager:
    """Simple JWT token manager without external dependencies"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def _base64_encode(self, data: bytes) -> str:
        """URL-safe base64 encode"""
        return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')
    
    def _base64_decode(self, data: str) -> bytes:
        """URL-safe base64 decode"""
        padding = 4 - len(data) % 4
        if padding != 4:
            data += '=' * padding
        return base64.urlsafe_b64decode(data)
    
    def create_token(self, payload: Dict[str, Any]) -> str:
        """Create a JWT token"""
        # Header
        header = {"alg": "HS256", "typ": "JWT"}
        header_b64 = self._base64_encode(json.dumps(header).encode('utf-8'))
        
        # Payload
        payload_b64 = self._base64_encode(json.dumps(payload).encode('utf-8'))
        
        # Signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        signature_b64 = self._base64_encode(signature)
        
        return f"{header_b64}.{payload_b64}.{signature_b64}"
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and verify a JWT token"""
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return None
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verify signature
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self.secret_key.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()
            
            actual_signature = self._base64_decode(signature_b64)
            
            if not hmac.compare_digest(expected_signature, actual_signature):
                return None
            
            # Decode payload
            payload = json.loads(self._base64_decode(payload_b64))
            
            # Check expiration
            if payload.get('exp', 0) < datetime.utcnow().timestamp():
                return None
            
            return payload
            
        except Exception as e:
            logger.error(f"Token decode error: {e}")
            return None


class UserDatabase:
    """Simple file-based user database"""
    
    def __init__(self):
        self.users_file = self._find_users_file()
        self.users: Dict[str, User] = {}
        self._load_users()
    
    def _find_users_file(self) -> Path:
        """Find or create users file"""
        for path in USERS_PATHS:
            if path.exists():
                return path
        
        # Create new file
        users_file = USERS_PATHS[0] if USERS_PATHS[0].parent.exists() else USERS_PATHS[1]
        users_file.write_text(json.dumps({"users": {}}))
        return users_file
    
    def _load_users(self):
        """Load users from file"""
        try:
            if self.users_file.exists():
                data = json.loads(self.users_file.read_text())
                for user_id, user_data in data.get("users", {}).items():
                    self.users[user_id] = User(**user_data)
                logger.info(f"✅ Loaded {len(self.users)} users from {self.users_file}")
        except Exception as e:
            logger.error(f"❌ Error loading users: {e}")
            self.users = {}
    
    def _save_users(self):
        """Save users to file"""
        try:
            data = {"users": {uid: user.to_dict() for uid, user in self.users.items()}}
            self.users_file.write_text(json.dumps(data, indent=2))
            logger.info(f"✅ Saved {len(self.users)} users to {self.users_file}")
        except Exception as e:
            logger.error(f"❌ Error saving users: {e}")
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        email_lower = email.lower()
        for user in self.users.values():
            if user.email.lower() == email_lower:
                return user
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def create_user(self, email: str, password: str, name: str) -> User:
        """Create a new user"""
        # Check if email already exists
        if self.get_user_by_email(email):
            raise AuthError("Email already registered")
        
        # Create user
        user_id = secrets.token_hex(16)
        now = datetime.utcnow().isoformat()
        
        user = User(
            id=user_id,
            email=email.lower(),
            password_hash=PasswordHasher.hash_password(password),
            name=name,
            created_at=now,
            updated_at=now,
            is_active=True,
            profile=None,
            preferences={"theme": "system", "diet_tags": [], "notifications": True}
        )
        
        self.users[user_id] = user
        self._save_users()
        
        logger.info(f"✅ Created new user: {email}")
        return user
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> Optional[User]:
        """Update user data"""
        user = self.users.get(user_id)
        if not user:
            return None
        
        for key, value in updates.items():
            if hasattr(user, key) and key not in ['id', 'email', 'password_hash', 'created_at']:
                setattr(user, key, value)
        
        user.updated_at = datetime.utcnow().isoformat()
        self._save_users()
        
        return user
    
    def update_password(self, user_id: str, new_password: str) -> bool:
        """Update user password"""
        user = self.users.get(user_id)
        if not user:
            return False
        
        user.password_hash = PasswordHasher.hash_password(new_password)
        user.updated_at = datetime.utcnow().isoformat()
        self._save_users()
        
        return True
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        if user_id in self.users:
            del self.users[user_id]
            self._save_users()
            return True
        return False


class AuthService:
    """Authentication service handling login, registration, and token management"""
    
    def __init__(self):
        self.db = UserDatabase()
        self.jwt = JWTManager(SECRET_KEY)
        self.hasher = PasswordHasher()
    
    def register(self, email: str, password: str, name: str) -> Dict[str, Any]:
        """Register a new user"""
        # Validate input
        if not email or '@' not in email:
            raise AuthError("Invalid email address")
        
        if len(password) < 6:
            raise AuthError("Password must be at least 6 characters")
        
        if not name or len(name) < 2:
            raise AuthError("Name must be at least 2 characters")
        
        # Create user
        user = self.db.create_user(email, password, name)
        
        # Generate tokens
        tokens = self._generate_tokens(user)
        
        return {
            "user": user.to_public_dict(),
            "tokens": tokens,
            "message": "Registration successful"
        }
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login user and return tokens"""
        user = self.db.get_user_by_email(email)
        
        if not user:
            raise AuthError("Invalid email or password")
        
        if not self.hasher.verify_password(password, user.password_hash):
            raise AuthError("Invalid email or password")
        
        if not user.is_active:
            raise AuthError("Account is disabled")
        
        # Generate tokens
        tokens = self._generate_tokens(user)
        
        logger.info(f"✅ User logged in: {email}")
        
        return {
            "user": user.to_public_dict(),
            "tokens": tokens,
            "message": "Login successful"
        }
    
    def refresh_tokens(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        payload = self.jwt.decode_token(refresh_token)
        
        if not payload:
            raise AuthError("Invalid or expired refresh token")
        
        if payload.get('token_type') != TokenType.REFRESH:
            raise AuthError("Invalid token type")
        
        user = self.db.get_user_by_id(payload.get('user_id'))
        
        if not user or not user.is_active:
            raise AuthError("User not found or disabled")
        
        # Generate new tokens
        tokens = self._generate_tokens(user)
        
        return {
            "tokens": tokens,
            "message": "Tokens refreshed"
        }
    
    def verify_token(self, token: str) -> Optional[User]:
        """Verify access token and return user"""
        payload = self.jwt.decode_token(token)
        
        if not payload:
            return None
        
        if payload.get('token_type') != TokenType.ACCESS:
            return None
        
        user = self.db.get_user_by_id(payload.get('user_id'))
        
        if not user or not user.is_active:
            return None
        
        return user
    
    def get_current_user(self, token: str) -> Dict[str, Any]:
        """Get current user from token"""
        user = self.verify_token(token)
        
        if not user:
            raise AuthError("Invalid or expired token")
        
        return user.to_public_dict()
    
    def update_profile(self, token: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        user = self.verify_token(token)
        
        if not user:
            raise AuthError("Invalid or expired token")
        
        # Update user profile
        updated_user = self.db.update_user(user.id, {"profile": profile_data})
        
        if not updated_user:
            raise AuthError("Failed to update profile")
        
        return {
            "user": updated_user.to_public_dict(),
            "message": "Profile updated"
        }
    
    def update_preferences(self, token: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Update user preferences"""
        user = self.verify_token(token)
        
        if not user:
            raise AuthError("Invalid or expired token")
        
        # Merge with existing preferences
        current_prefs = user.preferences or {}
        current_prefs.update(preferences)
        
        updated_user = self.db.update_user(user.id, {"preferences": current_prefs})
        
        if not updated_user:
            raise AuthError("Failed to update preferences")
        
        return {
            "user": updated_user.to_public_dict(),
            "message": "Preferences updated"
        }
    
    def change_password(self, token: str, old_password: str, new_password: str) -> Dict[str, Any]:
        """Change user password"""
        user = self.verify_token(token)
        
        if not user:
            raise AuthError("Invalid or expired token")
        
        # Verify old password
        if not self.hasher.verify_password(old_password, user.password_hash):
            raise AuthError("Current password is incorrect")
        
        # Validate new password
        if len(new_password) < 6:
            raise AuthError("New password must be at least 6 characters")
        
        # Update password
        self.db.update_password(user.id, new_password)
        
        return {"message": "Password changed successfully"}
    
    def _generate_tokens(self, user: User) -> Dict[str, str]:
        """Generate access and refresh tokens"""
        now = datetime.utcnow()
        
        # Access token
        access_payload = {
            "user_id": user.id,
            "email": user.email,
            "token_type": TokenType.ACCESS,
            "iat": now.timestamp(),
            "exp": (now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()
        }
        
        # Refresh token
        refresh_payload = {
            "user_id": user.id,
            "email": user.email,
            "token_type": TokenType.REFRESH,
            "iat": now.timestamp(),
            "exp": (now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)).timestamp()
        }
        
        return {
            "access_token": self.jwt.create_token(access_payload),
            "refresh_token": self.jwt.create_token(refresh_payload),
            "token_type": "Bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }


# Global auth service instance
auth_service = AuthService()
