<h4 align="center"> 
<img src="https://github.com/user-attachments/assets/581a0b9b-ea95-4651-a6db-64925e60a0bf" alt="long" border="0">
</h4>

<h1 align="center">
<img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white"/>
<img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=flat&logo=pytorch&logoColor=white"/>
<img src="https://img.shields.io/badge/Ultralytics-111F68?style=flat&logo=ultralytics&logoColor=white"/>
<img src="https://img.shields.io/badge/Amazon S3-569A31?style=flat&logo=amazons3&logoColor=white"/>
</h1>

# 📱Checkstagram FastAPI 백엔드
AI 기반 셀럽 SNS 사전 체크 솔루션 앱인 Checkstagram의 백엔드 서버입니다. 자연어 처리의 BERT 모델과 컴퓨터 비전의 YOLOv8, ResNet18 모델을 활용하여 SNS 이미지/영상/텍스트 콘텐츠를 사전 분석하고 욕설 텍스트 및 담배, 술, 브랜드 로고 등 민감한 정보가 포함된 콘텐츠를 사전에 감지하는 기능을 제공합니다.

## 📍 주요 기능
* 업로드 할 피드 콘텐츠인 이미지, 영상, 텍스트 분석 지원
  * 사용자가 선택한 카테고리 기반 필터링 분석
  * BERT 기반 모델을 활용한 피드 설명 텍스트(Description) 검열
  * YOLOv8 기반 객체 탐지 - (담배, 술, 가방, 폰, 콜라)
  * ResNet18 기반 브랜드 세부 분류 (ex 가방-루이비통, 폰-갤럭시)
* 분석 결과 S3 업로드 및 프론트에 URL 반환

## 📍 API 명세서

## 📁 디렉토리 구조
```
Checkstagram_fastapi/
├── app/
│   ├── main.py               # FastAPI 메인 서버
│   ├── config.py
│   ├── inference/            # 전체 추론 파이프라인
│   ├── model/                # BERT, YOLO, ResNet18 유틸
│   ├── services/             # S3 업로드, 카테고리 매핑
│   ├── static/               # 영상 분석 결과 저장 - Git 미포함
│   ├── assets/fonts          # 분석 결과 폰트 지정 - Git 미포함
├── weights/                  # 모델 가중치 (bert/yolov8/resnet18) - Git 미포함
├── requirements.txt
└── .env                      # 환경 변수 (비공개)
```

## ⚙️ 실행 방법

1. 프로젝트 클론
```
$ git clone https://github.com/checkmate12345/Checkstagram_fastapi.git
$ cd Checkstagram_fastapi
```

2. 가상환경 구성
```
$ python -m venv venv
$ source venv/bin/activate
```

3. 의존성 설치
```
$ pip install -r requirements.txt
```

4. 환경 변수 파일 생성(비공개)
   
   루트 디렉토리에 .env 파일을 생성하고 아래와 같은 환경 변수를 설정하세요. 하단의 내용은 **예시**입니다!
```
# AWS S3 설정
S3_BUCKET_NAME=your-s3-bucket-name
S3_BUCKET_DIRECTORY=checkstagram/feed-check
LOCAL_RESULTS_DIR=results

AWS_ACCESS_KEY=your-aws-access-key
AWS_SECRET_KEY=your-aws-secret-key
AWS_REGION=ap-northeast-2

# 애플리케이션 설정
DEBUG=True
PORT=8000

# 모델 관련 설정
# YOLO coarse 모델
YOLO_WEIGHT_PATH=./weights/best.pt
# ResNet fine 모델
RESNET_WEIGHT_PATH=./weights/resnet18.pt
CLASS_MAP_JSON=./weights/class_to_idx.json
# NLP 모델
TEXT_FILTER_MODEL_DIR=./weights/text_filter

# 객체 탐지 분석 결과 기준치 설정
YOLO_CONF_THRESHOLD=0.25
RESNET_CONF_THRESHOLD=70.0
```

5. 서버 실행
```
$ uvicorn app.main:app --host 0.0.0.0 --port 8000
```

-----------------

# 모델 학습 정보
Checkstagram의 콘텐츠 사전 체크 AI는 총 세 가지의 모델로 구성되어 있습니다.

## 1. 객체 탐지: YOLOv8
* 프레임워크: Ultralytics YOLOv8
* 기반 모델: yolov8n.pt (사전학습된 YOLOv8 nano)
* 파인튜닝 방식: 5개 클래스(Custom Dataset)로 전체 레이어 학습
* 학습 데이터: 커스텀 라벨링된 5개 클래스 당 약 30개의 이미지
  * cigarette, alcohol, bag, phone, coke
* 하이퍼파라미터:
  * Epoch: 50 (Early Stop 적용)
  * Optimizer: SGD
  * Image size: 640x640
* 데이터 증강: Mosaic, HSV, Scaling 등 Ultralytics 기본 augment 적용
* 성능:
  * mAP50: 67.3%
  * precision: 0.78, recall: 0.64 (검증 기준)

## 2. 탐지된 객체 세부 분류: ResNet18
* 기능: YOLO로 검출된 객체를 기반으로 가방, 폰, 콜라가 탐지되었다면 이를 세부 브랜드로 분류합니다. (ex 가방-샤넬, 폰-아이폰, 콜라-펩시)
* 기반 모델: torchvision 제공 resnet18(pretrained=True)
* 파인튜닝 방식: 최종 FC layer 수정 및 전체 레이어 학습
* 학습 데이터: 세부 분류 클래스 당 이미지 수 약 60개
  * bag: chanel, dior, gucci, hermes, louisvuitton
  * phone: iphone, galaxy
  * coke: cocacola, pepsi
* 하이퍼파라미터
  * Epoch: 30 (Early Stop 적용)
  * Batch size: 32
  * Loss: CrossEntropyLoss
  * Optimizer: Adam
* 전처리:
  * Resize (224x224), Normalize
  * Augmentation: Horizontal Flip, RandomCrop
* 성능:
  * Train accuracy: 94%
  * Val accuracy: 약 73.5%

## 3. 피드 Description 필터링: BERT

## 모델 학습 방향 및 한계
본 프로젝트는 포트폴리오 및 학습 목적의 커스텀 데이터셋을 기반으로 진행되었기 때문에 양질의 데이터 구축에 어려움이 있어 현 시점에서의 각 모델은 다음과 같은 한계를 가집니다.
* YOLO, ResNet
  * 학습 데이터 수가 충분하지 않아 일부 클래스 간 혼동 유발
  * 클래스 불균형에 따른 분류 정확도 편차
  * 객체 구분 성능은 조명, 배경에 따라 달라질 수 있음
* BERT
> 이를 개선하고자 프로젝트 구성원들은 아래의 내용을 시도하였습니다.

1️⃣ 최대한 다양한 모델 파인튜닝 전략을 실험적으로 적용

2️⃣ 모델 성능 최적화보다는 파이프라인 설계 및 프론트와의 모델 연동 역량에 집중된 실무형 AI 서비스 구조 설계
