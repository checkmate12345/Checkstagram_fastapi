from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
import uuid, os, json

from app.config import UPLOAD_DIR, RESULT_DIR, CATEGORY_KR_TO_EN
from app.service.pipeline import process_image, process_video
from app.service.s3_uploader import upload_to_s3
from app.service.text_filter import analyze_text_lines

router = APIRouter()

@router.post("/predict")
async def predict_feed(
    medias: List[UploadFile] = File(...),
    mediasMeta: str = Form(...),
    categories: str = Form(...),
    description: Optional[str] = Form(None)
):
    try:
        # JSON 문자열 파싱
        try:
            meta_info = json.loads(mediasMeta)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="mediasMeta 필드는 올바른 JSON 형식이어야 합니다")

        try:
            user_categories = json.loads(categories)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="categories 필드는 올바른 JSON 형식이어야 합니다")

        if len(medias) != len(meta_info):
            raise HTTPException(status_code=400, detail="medias와 mediasMeta의 항목 수가 일치하지 않습니다")

        # 1. 사용자 선택 항목 → 영문 클래스 리스트로 매핑
        target_class_names = []
        for cat_list in user_categories.values():
            for item in cat_list:
                eng = CATEGORY_KR_TO_EN.get(item)
                if eng:
                    target_class_names.append(eng)

        # 디렉토리 준비
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        os.makedirs(RESULT_DIR, exist_ok=True)

        all_results = []

        # 2. 각 미디어 파일 처리
        for idx, file in enumerate(medias):
            media_type = meta_info[idx]['mediaType']
            filename = f"{uuid.uuid4()}_{file.filename}"
            input_path = os.path.join(UPLOAD_DIR, filename)

            with open(input_path, 'wb') as f:
                f.write(await file.read())

            result_path, detected_labels = None, []
            timeline = None

            if media_type == 'image':
                result_path, detected_labels = process_image(input_path, target_class_names)
            elif media_type == 'video':
                result_path, detected_labels, timeline = process_video(input_path, target_class_names)
            else:
                raise HTTPException(status_code=400, detail=f"지원하지 않는 mediaType: {media_type}")

            # 3. S3 업로드
            result_url = upload_to_s3(result_path)

            result_obj = {
                "mediaType": media_type,
                "resultUrl": result_url,
                "resultObject": ", ".join(detected_labels)
            }
            if timeline:
                result_obj["timeline"] = timeline

            all_results.append(result_obj)

        # 4. description 텍스트 검열 처리
        censured_sentences = analyze_text_lines(description) if description else []

        return JSONResponse({
            "success": True,
            "message": "피드 검사에 성공했습니다",
            "description": description,
            "censuredSentences": censured_sentences,
            "results": all_results
        })

    except HTTPException as he:
        raise he
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": f"서버 오류: {str(e)}"
        })