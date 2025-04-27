# -*- coding: utf-8 -*-

from __init__ import *
import cv2
from pathlib import Path
from cnocr import CnOcr

ocr = CnOcr(
    rec_model_name="number-densenet_lite_136-fc",
    threshold=0.35,
)


def ocr_file(frame, path, save=False):
    pre_ext = op.splitext(op.basename(path))[0]
    ret = []

    def _ocr(w1, w2, h1, h2):
        text = ocr.ocr_for_single_line(frame[w1:w2, h1:h2])['text']
        if save:
            cv2.imwrite(f"output/test_{pre_ext}_{text}.jpg", f)
        ret.append(text)

    _ocr(931, 1000, 779, 893)
    _ocr(931, 1000, 1191, 1305)

    if len(ret) == 2:
        return "_".join(ret)


def save_vedio(path, out_path, ft, fe):
    src_cap = cv2.VideoCapture(path)
    out_cap = cv2.VideoWriter(
        out_path,
        cv2.VideoWriter_fourcc(*'avc1'),
        src_cap.get(cv2.CAP_PROP_FPS),
        (
            int(src_cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(src_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        ),
    )

    src_cap.set(cv2.CAP_PROP_POS_FRAMES, ft)
    while src_cap.isOpened():
        ret, frame = src_cap.read()
        if not ret or ft >= fe:
            break
        ft += 1
        out_cap.write(frame)

    out_cap.release()
    log(f"得分片段: {path} > {out_path}")


def check_dir(out_dir):
    for root, _, files in os.walk(out_dir):
        for file in files:
            try:
                parts = op.splitext(file)[0].split("_")
                assert int(parts[2]) >= int(parts[0]), "得分片段错误"
                assert int(parts[3]) >= int(parts[1]), "得分片段错误"
            except:
                log(f"非法:{op.join(root,file)} {parts}")


def ocr_video(path, out_dir, rate=1):
    video_exts = ('.mp4', '.avi', '.mov', '.mkv')
    if not path.lower().endswith(video_exts):
        return

    ext = op.splitext(path)[1]
    cap = cv2.VideoCapture(path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    fc = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    pre_score, score = None, None
    for ft in range(0, fc, fps * rate):
        cap.set(cv2.CAP_PROP_POS_FRAMES, ft)
        ret, frame = cap.read()
        if not ret:
            break

        score = ocr_file(frame, path)
        if not score:
            continue
        elif not pre_score:
            pre_score = score
        elif score != pre_score:
            out_path = op.join(out_dir, f"{pre_score}_{score}") + ext
            start = max(0, ft - 7 * fps)
            end = min(ft + fps, fc)
            save_vedio(path, out_path, start, end)
            break
    cap.release()


def generate(out_dir, *args):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    for dir in [*args]:
        if op.isdir(dir):
            for file in os.listdir(dir):
                path = op.join(dir, file)
                ocr_video(path, out_dir)
        elif op.isfile(dir):
            ocr_video(dir, out_dir)

    check_dir(out_dir)


if __name__ == "__main__":
    out_dir = "output/25.4.25白胜"
    generate(out_dir, "userdata/4.25白队", "userdata/4.25紫队")
