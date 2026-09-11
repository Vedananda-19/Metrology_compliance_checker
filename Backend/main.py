from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

allowed_origins = ["http://localhost:5173"]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_headers=["*"],
    allow_methods=["*"],
    allow_credentials=True,
)


@app.get("/")
def home():
    return "Home"
