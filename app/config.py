import os
from dotenv import load_dotenv

load_dotenv()

YOLO_WEIGHT_PATH = os.getenv("YOLO_WEIGHT_PATH")
RESNET_WEIGHT_PATH = os.getenv("RESNET_WEIGHT_PATH")
CLASS_MAP_JSON = os.getenv("CLASS_MAP_JSON")
TEXT_FILTER_MODEL_DIR = os.getenv("TEXT_FILTER_MODEL_DIR")

YOLO_CONF_THRESHOLD = float(os.getenv("YOLO_CONF_THRESHOLD"))
RESNET_CONF_THRESHOLD = float(os.getenv("RESNET_CONF_THRESHOLD"))

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_BUCKET_DIRECTORY = os.getenv("S3_BUCKET_DIRECTORY")

UPLOAD_DIR = "./app/static/uploads"
RESULT_DIR = "./app/static/results"

# app/config.py
FONT_PATH = "app/assets/fonts/Roboto-Variable.ttf"

# coarse 클래스 매핑 (YOLO 기준)
COARSE_CLASS_MAP = {
    0: "alcohol",
    1: "cigarette",
    2: "bag",
    3: "phone",
    4: "coke"
}

# fine 분류 대상 coarse 클래스 ID
NEEDS_FINE = [2, 3, 4]

CATEGORY_KR_TO_EN = {
    "담배": "cigarette",
    "술": "alcohol",
    "가방": "bag",
    "폰": "phone",
    "콜라": "coke",
    "구찌": "gucci",
    "루이비통": "louisvuitton",
    "샤넬": "chanel",
    "디올": "dior",
    "에르메스": "hermes",
    "아이폰": "iphone",
    "갤럭시": "galaxy",
    "펩시": "pepsi",
    "코카콜라": "cocacola"
}

SPECIAL_CLASSES = ["alcohol", "cigarette"]

FINE_TO_COARSE = {
    "chanel": "bag",
    "dior": "bag",
    "gucci": "bag",
    "hermes": "bag",
    "louisvuitton": "bag",
    "iphone": "phone",
    "galaxy": "phone",
    "cocacola": "coke",
    "pepsi": "coke"
}