# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import predict
import os

app = FastAPI(title="Feed Inspection AI API")

# CORS 설정 (프론트엔드 개발 시 필요)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 배포 시 도메인 제한 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(predict.router)

# 초기 디렉토리 생성 (uploads, results)
os.makedirs("./app/static/uploads", exist_ok=True)
os.makedirs("./app/static/results", exist_ok=True)

@app.get("/")
def root():
    return {"message": "FastAPI 연동 테스트"}