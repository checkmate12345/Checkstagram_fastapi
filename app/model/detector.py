from ultralytics import YOLO
from app.config import YOLO_WEIGHT_PATH

# YOLO 모델 불러오기
yolo_model = YOLO(YOLO_WEIGHT_PATH)

def detect_objects(image, conf=0.25):
    results = yolo_model.predict(image, save=False, conf=conf)
    return results[0].boxes