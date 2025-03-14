import cv2
import numpy as np

prototxt_path = "models/deploy.prototxt"
model_path = "models/res10_300x300_ssd_iter_140000_fp16.caffemodel"
net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)

def detect_faces_and_speakers(input_video_path, output_video_path):
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {input_video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    width, height = int(cap.get(3)), int(cap.get(4))
    if width <= 0 or height <= 0:
        raise ValueError(f"Invalid dimensions: {width}x{height}")
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        # Skip invalid frames
        if frame is None or frame.size == 0 or frame.shape[0] <= 0 or frame.shape[1] <= 0:
            out.write(np.zeros((height, width, 3), dtype=np.uint8))  # Blank frame
            continue
        # Resize safely
        try:
            small_frame = cv2.resize(frame, (150, 150), interpolation=cv2.INTER_AREA)
            blob = cv2.dnn.blobFromImage(small_frame, 1.0, (150, 150), (104.0, 177.0, 123.0))
            net.setInput(blob)
            detections = net.forward()
            # No drawing - just detection
            for i in range(detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                if confidence > 0.5:
                    pass  # Detection happens, no box
        except cv2.error as e:
            print(f"Frame processing error: {e}")
            out.write(frame)  # Write original frame on error
            continue
        out.write(frame)
    cap.release()
    out.release()
    print(f"Face detection completed: {output_video_path}")