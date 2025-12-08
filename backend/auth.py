# auth.py
from fastapi import FastAPI, Request, Depends, HTTPException, APIRouter
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
import os
from jose import jwt
import datetime
from fastapi.middleware.cors import CORSMiddleware

JWT_SECRET = os.getenv("JWT_SECRET", "supersecretkey")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60

router = APIRouter()
# OAuth setup
oauth = OAuth()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
CONF_URL = "https://accounts.google.com/.well-known/openid-configuration"

oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url=CONF_URL,
    client_kwargs={"scope": "openid email profile",
                   "access_type": "offline",
                   "prompt":"select_account"}
)

# Temporary store for sessions (replace with database in production)

# user_sessions = {}

# print(user_sessions)

@router.get("/login")
async def login(request: Request):
    redirect_uri = "http://127.0.0.1:8000/callback"  # Streamlit redirect URI
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/callback")
async def callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    # user = await oauth.google.parse_id_token(request, token)
    try:
        user = await oauth.google.parse_id_token(request, token)
    except Exception:
        user = await oauth.google.userinfo(token=token)
    if not user:
        raise HTTPException(status_code=400, detail="Authentication failed")
    # Create JWT token
    payload = {

        "name":user["given_name"],
        "sub": user["email"],  # user identity
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=JWT_EXPIRE_MINUTES)
    }
    jwt_token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    # Save token for session
    # user_sessions[user["email"]] = token["access_token"]
    # Redirect back to Streamlit
    # return RedirectResponse(url=f"http://127.0.0.1:8000/?user={user['email']}")
    return RedirectResponse(url=f"http://localhost:8501/?token={jwt_token}")

# @router.get("/session_token")
# def get_session(email:str):
#     print("user_sessions")
#     print(user_sessions)
#     token = user_sessions.get(email)
#     if token:
#         return {"token":token}
#     raise HTTPException(status_code=404, detail="Token not found")