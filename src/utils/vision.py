# -*- coding: utf-8 -*-

import json
import os
import shutil
import cv2
from pathlib import Path
from openai import OpenAI
from ultralytics import YOLO
from time import time

# 初始化模型
yolo_model = YOLO('assets/yolov8s.pt')  # 球员检测模型
openpose_proto = "assets/pose_deploy_linevec.prototxt"
openpose_model = "assets/pose_iter_440000.caffemodel"
pose_net = cv2.dnn.readNetFromCaffe(openpose_proto, openpose_model)

# 配置参数
FRAME_INTERVAL = 3  # 每秒1帧

# 在文件开头添加骨骼连接配置
POSE_PAIRS = [
    (1, 2),
    (1, 5),
    (2, 3),
    (3, 4),
    (5, 6),
    (6, 7),  # 手臂
    (1, 8),
    (8, 9),
    (9, 10),  # 右腿
    (1, 11),
    (11, 12),
    (12, 13),  # 左腿
    (1, 0),
    (0, 14),
    (14, 16),
    (0, 15),
    (15, 17)  # 面部和躯干
]


def clear_output(output_dir):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)


def analyze_pose(frame, box):
    """对单个球员进行姿态分析"""
    x1, y1, x2, y2 = map(int, box)
    player_img = frame[y1:y2, x1:x2]

    blob = cv2.dnn.blobFromImage(
        player_img,
        1.0 / 255,
        (368, 368),
        (0, 0, 0),
        swapRB=False,
        crop=False,
    )
    pose_net.setInput(blob)
    pose_output = pose_net.forward()

    pose = []
    H, W = player_img.shape[:2]
    for j in range(18):
        prob_map = pose_output[0, j, :, :]
        prob_map = cv2.resize(prob_map, (W, H))
        prob_map = cv2.GaussianBlur(prob_map, (3, 3), 0)

        _, confidence, _, point = cv2.minMaxLoc(prob_map)
        if confidence > 0.2:
            x = x1 + point[0]
            y = y1 + point[1]
            pose.append((int(x), int(y)))
        else:
            pose.append(None)
    return pose


def detect_players(frame):
    """检测并跟踪球员"""
    results = yolo_model.track(frame, persist=True, classes=[0])
    boxes = results[0].boxes.xyxy.cpu().numpy()
    track_ids = []
    if results[0].boxes.id is not None:
        track_ids = results[0].boxes.id.int().cpu().numpy()
    return boxes, track_ids


def process_frame(frame, frame_count, timestamp, output_dir):
    """处理单帧图像"""
    # 保存帧数据
    frame_filename = f"{output_dir}/frame_{timestamp:.1f}_{frame_count}.jpg"
    cv2.imwrite(frame_filename, frame)

    # 球员检测和姿态分析
    boxes, track_ids = detect_players(frame)
    players = []
    frame_keypoints = []

    for box, track_id in zip(boxes, track_ids):
        pose = analyze_pose(frame, box)
        position = [int((box[0] + box[2]) / 2), int((box[1] + box[3]) / 2)]

        player_data = {
            'id': int(track_id),
            'position': position,
            'box': box.tolist(),
            'pose': pose
        }
        players.append(player_data)
        frame_keypoints.append(pose)

    return players, frame_keypoints


def draw_player(frame, player):
    """绘制单个球员的边界框和ID"""
    box = player['box']
    cv2.rectangle(frame, (int(box[0]), int(box[1])),
                  (int(box[2]), int(box[3])), (0, 255, 255), 2)

    cv2.putText(frame, f"ID: {player['id']}", (int(box[0]), int(box[1]) - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)


def draw_skeleton(frame, keypoints):
    """绘制骨骼结构"""
    for point in keypoints:
        if point is not None:
            cv2.circle(frame, point, 3, (0, 255, 0), -1)

    for pair in POSE_PAIRS:
        partA = keypoints[pair[0]]
        partB = keypoints[pair[1]]
        if partA is not None and partB is not None:
            cv2.line(frame, partA, partB, (0, 0, 255), 2)


def process_video(video_path):
    output_dir = f"output/{Path(video_path).stem}"
    clear_output(output_dir)

    events = []
    frames = []
    all_keypoints = []
    actions = []

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * FRAME_INTERVAL)

    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval != 0:
            frame_count += 1
            continue

        frames.append(frame.copy())
        timestamp = frame_count / fps

        players, frame_keypoints = process_frame(frame, frame_count, timestamp,
                                                 output_dir)

        all_keypoints.append(frame_keypoints)
        actions.append(f"Frame {frame_count}")
        events.append({'time': round(timestamp, 1), 'players': players})
        frame_count += 1

    cap.release()
    return events, frames, all_keypoints, actions


def visualize_results(frames, keypoints, actions):
    for i, frame in enumerate(frames):
        if i < len(events):
            for player in events[i]['players']:
                draw_player(frame, player)

        if i < len(keypoints):
            for person_keypoints in keypoints[i]:
                draw_skeleton(frame, person_keypoints)

        cv2.putText(frame, actions[i], (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 0, 255), 2)

        cv2.imshow('Basketball Action Analysis', frame)
        if cv2.waitKey(1000) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()


def llm_analysis(events):
    LLM_API_URL = "http://localhost:11434/v1/"
    MODEL = "deepseek-r1:32b"
    API_KEY = "ollama"
    """增强的大模型提示词"""
    str_events = json.dumps(events, ensure_ascii=False, indent=2)
    prompt = f"""作为专业篮球分析师，请分析以下事件:
1. 得分判定需同时满足:
   - 投篮动作检测有效
   - 篮球轨迹进入篮筐区域
2. 抢断判定需满足:
   - 防守方突然移动
   - 球权发生明显转移
事件数据:
{str_events}
请输出:1) 得分球员及次数 2) 抢断统计 3) 关键事件时间线"""

    client = OpenAI(base_url=LLM_API_URL, api_key=API_KEY)
    create = client.chat.completions.create
    messages = [{"role": "user", "content": prompt}]
    response = create(
        model=MODEL,
        messages=messages,
        max_tokens=3000,
        temperature=0.2,
    )
    return response.choices[0].message.content


def llm_descrip(
    image_path,
    system="请详细描述这张图片的内容,比如谁在投篮,谁在防守等等",
    content=None,
):
    try:
        if not content:
            assert os.path.exists(image_path), f"图片不存在: {image_path}"
            with open(image_path, "rb") as f:
                content = base64.b64encode(f.read()).decode('utf-8')

        image_url = {"url": f"data:image/jpeg;base64,{content}"}
        prompt = {"type": "text", "text": system}
        image = {"type": "image_url", "image_url": image_url}
        messages = [{"role": "user", "content": [prompt, image]}]
        client = OpenAI(base_url=base_url, api_key=api_key)
        create = client.chat.completions.create
        response = create(model=model, messages=messages, max_tokens=3000)
        return response.choices[0].message.content
    except Exception as e:
        print(e)


if __name__ == "__main__":
    path = '.res/宏伟-004.mp4'

    # 处理视频生成事件序列
    ti = time()
    events, frames, keypoints, actions = process_video(path)
    print(f"视频处理完成, 耗时 {time()-ti:.1f}秒")

    # 调用可视化函数
    visualize_results(frames, keypoints, actions)

    # 大模型分析
    # analysis_result = llm_analysis(events)
    # print("\n大模型分析结果: {analysis_result}")
