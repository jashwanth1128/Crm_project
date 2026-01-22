
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, ValidationError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

try:
    print("Testing password hash...")
    pw = "admin123"
    hashed = get_password_hash(pw)
    print(f"Hash success: {hashed}")
    verified = verify_password(pw, hashed)
    print(f"Verify success: {verified}")
except Exception as e:
    print(f"Hash/Verify failed: {e}")

# Test Model
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

try:
    print("Testing LoginRequest model...")
    data = {"email": "admin@crm.com", "password": "admin123"}
    model = LoginRequest(**data)
    print(f"Model validation success: {model}")
except Exception as e:
    print(f"Model validation failed: {e}")
