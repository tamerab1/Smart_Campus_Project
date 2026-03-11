# --- Imports ---
# Gathering all necessary modules for the API and Database
from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.core.database import engine, Base
from app.routes import ask_route
from app.routes import admin
import app.models.campus 

# --- App Initialization ---
# Creating the database tables if they don't exist
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Smart Campus Assistant")

app.include_router(admin.router)
# Mounting static files (CSS/JS) and setting up templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# --- Security & Auth ---
# Simple basic auth setup for the admin dashboard
security = HTTPBasic()

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    # TODO: Replace hardcoded credentials with a secure check against the DB
    if credentials.username != "admin" or credentials.password != "password123":
        raise HTTPException(
            status_code=401,
            detail="Unauthorized access",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# --- Routes ---
# Including API router
app.include_router(ask_route.router)

# Home page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Chat interface
@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})
