from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F
import os

from app.config import TEXT_FILTER_MODEL_DIR  # 경로 변수명 수정됨

# Load model and tokenizer
model = AutoModelForSequenceClassification.from_pretrained(TEXT_FILTER_MODEL_DIR)
tokenizer = AutoTokenizer.from_pretrained(TEXT_FILTER_MODEL_DIR)
model.eval()

# Class id for 'ETHICAL' (정상 문장)
ETHICAL_CLASS_ID = model.config.label2id.get("ETHICAL", 7)

def analyze_text(text: str):
    """한 개의 문장을 분석해 비윤리 여부 반환"""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=256)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = F.softmax(outputs.logits, dim=1)
        pred = torch.argmax(probs, dim=1).item()
        return {
            "text": text,
            "censured": pred != ETHICAL_CLASS_ID
        }

def analyze_text_lines(description: str):
    """description 문자열을 \n 단위로 나누고 각각 분석"""
    sentences = [line.strip() for line in description.split("\n") if line.strip()]
    return [analyze_text(sentence) for sentence in sentences]