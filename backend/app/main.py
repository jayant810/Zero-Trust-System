from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, protected

app = FastAPI(title="Zero Trust Authentication System")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For demo purposes, we allow all. Adjust for production.
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
