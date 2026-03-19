"""
This is the FastAPI endpoint
Author: Aarti Dashore
Version: 1.0.0
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from routers import businesses, deals, reviews
from database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="CommunitySpark", version="1.0.0", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(businesses.router, prefix="/api/businesses", tags=["businesses"])
app.include_router(deals.router, prefix="/api/deals", tags=["deals"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["reviews"])


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/deals")
async def deals_page(request: Request):
    return templates.TemplateResponse("deals.html", {"request": request})


@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/business/{business_id}")
async def business_page(request: Request, business_id: int):
    return templates.TemplateResponse(
        "business.html", {"request": request, "business_id": business_id}
    )
