# app/main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.routes import ask_route
from app.database import engine, Base
import app.models.campus 

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Campus Assistant")

# Mount the static directory to serve CSS, JS, Images, etc.
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# Include our API routing
app.include_router(ask_route.router)

# Serve the web interface on the root URL
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})