# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from backend.routes import auth, users, agreements, chat, ratings, admin
from backend.database.db import create_tables

app = FastAPI(title="SkillSwap Africa API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(agreements.router)
app.include_router(chat.router)
app.include_router(ratings.router)
app.include_router(admin.router)

@app.on_event("startup")
def startup_event():
    create_tables()
    from backend.database.db import SessionLocal
    from backend.models.user import User
    from backend.utils.auth import hash_password
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.is_admin == True).first():
            db.add(User(full_name="SkillSwap Admin", email="admin@skillswap.africa", hashed_password=hash_password("admin123"), is_admin=True, language="english"))
            db.commit()
            print("✅ Admin created: admin@skillswap.africa / admin123")
    finally:
        db.close()

@app.get("/")
def root(): return {"app": "SkillSwap Africa", "status": "running", "docs": "/docs"}

@app.get("/health")
def health(): return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
