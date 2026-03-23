from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, protected
from app.utils.database import init_db
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Initialize Database (SQLite)
init_db()

# Rate Limiter Setup
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Zero Trust Authentication System")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(protected.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Zero Trust Secure API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
