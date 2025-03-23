import os
import uuid
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import torch
import torch.nn.functional as F

from app.config import YOLO_WEIGHT_PATH, RESNET_WEIGHT_PATH, CLASS_MAP_JSON, YOLO_CONF_THRESHOLD, RESNET_CONF_THRESHOLD, COARSE_CLASS_MAP, NEEDS_FINE, RESULT_DIR, FONT_PATH, SPECIAL_CLASSES, FINE_TO_COARSE
from app.model.detector import yolo_model, detect_objects
from app.model.classifier import resnet_model, resnet_transform, idx_to_class

font = ImageFont.truetype(FONT_PATH, 28)

def process_image(image_path, target_class_names):
    print("\n========== 이미지 예측 시작 ==========")
    print("필터 대상 (target_class_names):", target_class_names)

    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    detected_labels = []

    boxes = detect_objects(image, YOLO_CONF_THRESHOLD)
    print(f"(1) YOLO 탐지된 객체 수: {len(boxes)}")

    for box in boxes:
        cls_id = int(box.cls)
        coarse_label = COARSE_CLASS_MAP.get(cls_id, 'Unknown')
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        yolo_conf_pct = float(box.conf) * 100
        label = coarse_label
        draw_box = False

        print(f"\nYOLO 감지 → coarse_label: {coarse_label} ({yolo_conf_pct:.1f}%)")

        if coarse_label not in target_class_names and cls_id not in NEEDS_FINE:
            print("coarse_label 필터 통과 실패")
            continue

        if cls_id in NEEDS_FINE:
            roi = image.crop((x1, y1, x2, y2))
            roi_tensor = resnet_transform(roi).unsqueeze(0)
            with torch.no_grad():
                output = resnet_model(roi_tensor)
                probs = F.softmax(output, dim=1)
                pred_idx = torch.argmax(probs, dim=1).item()
                fine_label = idx_to_class[pred_idx]
                fine_conf_pct = probs[0][pred_idx].item() * 100
                print(f"(2) ResNet 예측 → {fine_label} ({fine_conf_pct:.1f}%)")

                if fine_label in target_class_names and fine_conf_pct >= RESNET_CONF_THRESHOLD:
                    coarse_label = FINE_TO_COARSE.get(fine_label, coarse_label)
                    label = f"{coarse_label} - {fine_label}"
                    draw_box = True
                    detected_labels.append(fine_label)
                else:
                    print("ResNet 조건 통과 실패")
        else:
            if yolo_conf_pct >= YOLO_CONF_THRESHOLD:
                draw_box = True
                detected_labels.append(coarse_label)

        if draw_box:
            color = "red" if coarse_label in SPECIAL_CLASSES else "green"
            draw.rectangle([x1, y1, x2, y2], outline=color, width=2)
            draw.text((x1, y1 - 30), f"{label} ({yolo_conf_pct:.1f}%)", font=font, fill=color)
            print(f"(3) 박스 그리기: {label}")

    output_path = os.path.join(RESULT_DIR, f"result_{uuid.uuid4()}.jpg")
    image.save(output_path)
    print(f"(4) 이미지 저장: {output_path}")
    print("========== 이미지 추론 끝 ==========")
    return output_path, list(set(detected_labels))

def process_video(video_path, target_class_names):
    print("\n========== 영상 추론 시작 ==========")
    print("필터 대상 (target_class_names):", target_class_names)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w, h = int(cap.get(3)), int(cap.get(4))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_path = os.path.join(RESULT_DIR, f"result_{uuid.uuid4()}.mp4")
    out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    detected_labels = []
    timeline_map = {}
    frame_idx = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(image)

        boxes = detect_objects(image, YOLO_CONF_THRESHOLD)
        print(f"\n(1) 프레임 내 YOLO 탐지 객체 수: {len(boxes)}")

        current_labels = set()

        for box in boxes:
            cls_id = int(box.cls)
            coarse_label = COARSE_CLASS_MAP.get(cls_id, 'Unknown')
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            yolo_conf_pct = float(box.conf) * 100
            label = coarse_label
            draw_box = False

            print(f"YOLO 감지 → coarse_label: {coarse_label} ({yolo_conf_pct:.1f}%)")

            if coarse_label not in target_class_names and cls_id not in NEEDS_FINE:
                print("coarse_label 필터 통과 실패")
                continue

            if cls_id in NEEDS_FINE:
                roi = image.crop((x1, y1, x2, y2))
                roi_tensor = resnet_transform(roi).unsqueeze(0)
                with torch.no_grad():
                    output = resnet_model(roi_tensor)
                    probs = F.softmax(output, dim=1)
                    pred_idx = torch.argmax(probs, dim=1).item()
                    fine_label = idx_to_class[pred_idx]
                    fine_conf_pct = probs[0][pred_idx].item() * 100
                    print(f"(2) ResNet 예측 → {fine_label} ({fine_conf_pct:.1f}%)")

                    if fine_label in target_class_names and fine_conf_pct >= RESNET_CONF_THRESHOLD:
                        coarse_label = FINE_TO_COARSE.get(fine_label, coarse_label)
                        label = f"{coarse_label} - {fine_label}"
                        draw_box = True
                        detected_labels.append(fine_label)
                        current_labels.add(fine_label)
                    else:
                        print("ResNet 조건 통과 실패")
            else:
                if yolo_conf_pct >= YOLO_CONF_THRESHOLD:
                    draw_box = True
                    detected_labels.append(coarse_label)
                    current_labels.add(coarse_label)

            if draw_box:
                color = "red" if coarse_label in SPECIAL_CLASSES else "green"
                draw.rectangle([x1, y1, x2, y2], outline=color, width=2)
                draw.text((x1, y1 - 30), f"{label} ({yolo_conf_pct:.1f}%)", font=font, fill=color)
                print(f"(3) 박스 그리기: {label}")

        for lbl in current_labels:
            timeline_map.setdefault(lbl, []).append(frame_idx)

        result_frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        out.write(result_frame)
        frame_idx += 1

    cap.release()
    out.release()
    print(f"(4) 영상 저장: {output_path}")
    print("========== 영상 추론 끝 ==========")

    timeline_result = {}
    for label, frames in timeline_map.items():
        ranges = []
        if not frames:
            continue
        start = prev = frames[0]
        for f in frames[1:]:
            if (f - prev) / fps > 1.0:
                ranges.append({"start": round(start / fps, 2), "end": round(prev / fps, 2)})
                start = f
            prev = f
        ranges.append({"start": round(start / fps, 2), "end": round(prev / fps, 2)})
        timeline_result[label] = ranges

    return output_path, list(set(detected_labels)), timeline_result