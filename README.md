1. 루트 경로 진입
cd checkstagram_fastapi

2. 가상환경 설정
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

3. 모듈 설치
pip install -r requirements.txt

4. 다시 루트 경로로 돌아가서 서버 실행
uvicorn app.main:app --reload