from ultralytics import YOLO
import cv2
import os
import keyboard
import time

# -----------------------------
# 1️⃣ 加载模型
# -----------------------------
model = YOLO("yolov8n.pt")  # nano版

# -----------------------------
# 2️⃣ 自动创建保存目录
# -----------------------------
os.makedirs("runs/image", exist_ok=True)
os.makedirs("runs/video", exist_ok=True)
os.makedirs("runs/camera", exist_ok=True)

# 获取时间戳，保证文件唯一
timestamp = int(time.time())

# -----------------------------
# 3️⃣ 图片检测
# -----------------------------
print("=== 图片检测 ===")
img_url = "https://ultralytics.com/images/bus.jpg"
results = model(img_url)
res_img = results[0]
res_img.show()

res_img_path = os.path.join("runs/image", f"bus_result_{timestamp}.jpg")
res_img.save(res_img_path)
print(f"图片检测完成，结果保存在 {res_img_path}")

# -----------------------------
# 4️⃣ 视频检测
# -----------------------------
video_path = "sample_video.mp4"
if os.path.exists(video_path):
    print("=== 视频检测 ===")
    cap = cv2.VideoCapture(video_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_path = os.path.join("runs/video", f"output_{timestamp}.mp4")
    out = cv2.VideoWriter(out_path, fourcc, 30.0,
                          (int(cap.get(3)), int(cap.get(4))))

    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        results = model(frame)[0]
        frame = results.plot()
        out.write(frame)

        if frame_count % 2 == 0:
            cv2.imshow("Video Detection", frame)
            cv2.waitKey(1)
        frame_count += 1

        if keyboard.is_pressed('q'):
            print("视频检测手动退出")
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"视频检测完成，结果保存在 {out_path}")
else:
    print("视频文件不存在，跳过视频检测")

# -----------------------------
# 5️⃣ 摄像头实时检测并保存视频
# -----------------------------
print("=== 摄像头实时检测 ===")
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

cam_out_path = os.path.join("runs/camera", f"camera_output_{timestamp}.mp4")
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out_cam = cv2.VideoWriter(cam_out_path, fourcc, 20.0, (640, 480))

try:
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        results = model(frame)[0]
        frame = results.plot()
        out_cam.write(frame)

        if frame_count % 2 == 0:
            cv2.imshow("Camera Detection", frame)
            cv2.waitKey(1)

        frame_count += 1
        if keyboard.is_pressed('q'):
            print("摄像头检测手动退出")
            break
finally:
    cap.release()
    out_cam.release()
    cv2.destroyAllWindows()
    print(f"摄像头资源已释放，检测视频保存在 {cam_out_path}")
