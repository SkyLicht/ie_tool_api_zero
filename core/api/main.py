import time
from datetime import timedelta

import jwt
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status
from starlette.middleware.cors import CORSMiddleware

from core.api.dependency import get_scoped_db_session
from core.api.endpoints import user_endpoint, router_endpoint
from core.api.endpoints.layout import layout_endpoint
from core.api.endpoints.line_balance import line_balance_endpoint
from core.api.endpoints.planner import planner_endpoint, platform_endpoint
from core.auth.security import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, SECRET_KEY, \
    ALGORITHM
from core.data.schemas.token_schema import Token
from core.db.ie_tool_db import IETOOLDBConnection
from core.logger_manager import LoggerManager


app = FastAPI()
# Allow CORS for localhost:3000
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:3000","http://10.13.33.46:3000","http://localhost:8000"],  # Adjust origins as needed
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    db = IETOOLDBConnection().get_session()
    # get user
    start_time = time.time()  # Record the start time of the request


    # Extract the Authorization header
    auth_header = request.headers.get("authorization")
    user = 'UNKNOWN'

    if auth_header and auth_header.startswith("Bearer "):
        user: str = jwt.decode(auth_header.split(" ")[1], SECRET_KEY, algorithms=[ALGORITHM]).get("sub")




    logger = LoggerManager.get_logger(name="FastAPI", log_file_name="request", username=user)
    try:
        request.state.db = db

        # Attempt to process the request
        response = await call_next(request)

        # Calculate the time taken for the request
        process_time = time.time() - start_time

        # Log the request information and response details
        logger.info(
            "Request: method=%s, url=%s, client=%s, status_code=%s, process_time=%.2f seconds",
            request.method,
            request.url.path,
            request.client.host,
            response.status_code,
            process_time
        )

        # db.commit()  # commit if everything succeeded
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
        # # Log the error with request details
        # logger.error(
        #     "Error: method=%s, url=%s, client=%s, error=%s",
        #     request.method,
        #     request.url.path,
        #     request.client.host,
        #     str(e)
        # )
    return response

app.include_router(
    prefix='/api/v1',
    router= user_endpoint.router
)

app.include_router(
    prefix='/api/v1',
    router= router_endpoint.router
)

app.include_router(
    prefix='/api/v1',
    router= planner_endpoint.router
)

app.include_router(
    prefix='/api/v1',
    router= platform_endpoint.router
)

app.include_router(
    prefix='/api/v1',
    router= layout_endpoint.router
)

app.include_router(
    prefix='/api/v1',
    router= line_balance_endpoint.router
)

@app.get("/")
async def read_root():
    return {"Hello": "World"}
@app.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_scoped_db_session)
):

    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
