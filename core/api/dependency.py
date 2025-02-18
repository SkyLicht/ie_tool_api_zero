from typing import List

import jwt
from fastapi import Depends, HTTPException, Request
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status

from core.auth.security import oauth2_scheme, SECRET_KEY, ALGORITHM
from core.data.models.it_tool_orm_models import UserModel
from core.data.repositroy.layout.layout_endpoint import LayoutRepository
from core.data.repositroy.line_balance.line_balance_repository import LineBalanceRepository
from core.data.repositroy.planner.line_repository import LineRepository
from core.data.repositroy.planner.work_day_repository import WorkDayRepository
from core.data.repositroy.planner.work_plan_repository import WorkPlanRepository
from core.data.repositroy.user_repository import UserRepository
from core.db.ie_tool_db import IETOOLDBConnection
from core.logger_manager import LoggerManager


def get_db(request: Request):
    return request.state.db


def get_scoped_db_session():
    db = IETOOLDBConnection().ScopedSession  # Get the ScopedSession instance

    try:
        yield db  # Provide the session to the caller
    except SQLAlchemyError as e:
        db.rollback()  # Rollback transaction in case of an exception
        raise e  # Re-raise the exception
    finally:
        db.remove()  # Call remove() to clear the thread-local session


def get_current_user(
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
) -> UserModel:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    logger = LoggerManager.get_logger(name="db", username=username)
    user_repo = UserRepository(db, logger)
    user = user_repo.get_user_by_username(username=username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# def check_permission(required_roles: List[str]):
#     """
#     Dependency that checks if the user has at least one of the required roles.
#     """
#     def role_checker(user: User = Depends(get_current_user)):
#         if user.role.name not in required_roles:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Not enough permissions"
#             )
#         return user
#     return role_checker


def get_planner_repository(db: Session = Depends(get_db), user: UserModel = Depends(get_current_user)):
    with WorkDayRepository(db, user) as repo:
        yield repo


def get_work_plan_repository(db: Session = Depends(get_db), user: UserModel = Depends(get_current_user)):
    with WorkPlanRepository(db, user) as repo:
        yield repo


def get_line_balance_repository(db: Session = Depends(get_db), user: UserModel = Depends(get_current_user)):
    with LineBalanceRepository(db, user) as repo:
        yield repo


def get_line_repository(
        db: Session = Depends(get_db),
        user: UserModel = Depends(get_current_user)
):
    with LineRepository(db, user) as repo:
        yield repo


def get_layout_repository(
        db: Session = Depends(get_db),
        user: UserModel = Depends(get_current_user)
):
    with LayoutRepository(db, user) as repo:
        yield repo
