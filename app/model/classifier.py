import torch
from torchvision import models, transforms
import json
from app.config import RESNET_WEIGHT_PATH, CLASS_MAP_JSON

# 클래스 인덱스 로드
with open(CLASS_MAP_JSON, 'r', encoding='utf-8') as f:
    class_to_idx = json.load(f)
idx_to_class = {v: k for k, v in class_to_idx.items()}

# ResNet 모델 로드
resnet_model = models.resnet18(pretrained=False)
resnet_model.fc = torch.nn.Linear(resnet_model.fc.in_features, len(class_to_idx))
resnet_model.load_state_dict(torch.load(RESNET_WEIGHT_PATH, map_location='cpu'))
resnet_model.eval()

# 전처리
resnet_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])