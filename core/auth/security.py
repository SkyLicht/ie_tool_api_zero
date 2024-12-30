from datetime import timedelta, datetime
from typing import Optional, List

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt  # pyjwt
from sqlalchemy.orm import Session

from core.auth.auth_utils import verify_password
from core.data.models.it_tool_orm_models import UserModel
from core.data.repositroy.user_repository import UserRepository
from core.data.schemas.user_schema import UserTranslate
from core.logger_manager import LoggerManager

# Secret key to encode JWT tokens
SECRET_KEY = "4f1dada27ca17e21e166dc7e7c8978e3d32d25832432b3fcde66e988c4c9de35"  # Replace with your own secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

logger_db = LoggerManager.get_logger(name="DatabaseLogger", log_file="config/logs/db.log", username="SYSTEM")


def authenticate_user(db: Session, username: str, password: str) -> Optional[UserModel]:
    user_repo = UserRepository(db, logger_db)
    user = user_repo.get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def check_permission(user: UserModel, required_route: List[str], required_permission: List[str]) :
    """
    Dependency that checks if the user has at least one of the required roles.
    """

    user_auth = UserTranslate.orm_to_user_auth(user).has_permission(required_route, required_permission)

    if not user_auth['has_route_access']:
        raise HTTPException(status_code=403, detail="Not enough router access")
    if not user_auth['has_permission']:
        raise HTTPException(status_code=403, detail="Not enough permissions")
