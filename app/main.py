from fastapi import FastAPI, Request, Depends
from app.routes.user_routes import router as user_router
from app.routes.remove_bg_route import router as remove_bg_router
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.utils.jwt_verification_always_pass import verify_token_always_pass


app = FastAPI()



# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://bg-remover.vikashkk.com"],
    # allow_origins=["*"],  # Allow all origins or specify a list of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Mount static files (for CSS, JS, images)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up Jinja2 template engine
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


app.include_router(user_router, prefix="/auth", tags=["Auth"])
app.include_router(remove_bg_router, prefix="/try", tags=["Try"], dependencies=[Depends(verify_token_always_pass)])
