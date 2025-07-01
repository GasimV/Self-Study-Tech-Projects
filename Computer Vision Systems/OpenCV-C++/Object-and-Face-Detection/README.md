# Object and Face Detection with OpenCV DNN

This project contains two separate C++ programs for object detection and face detection using OpenCV's Deep Neural Network (DNN) module. Each executable loads a pre-trained model and processes either an image or video stream to detect objects or faces.

---

## 🧠 Program 1: Object Detection (`DL.exe`)

This executable uses a YOLOv3-based model to perform general object detection on static images.

### 🔄 Workflow

1. Loads class labels from `coco.names`.
2. Initializes a YOLOv3 model using `yolov3.cfg` and `yolov3.weights`.
3. Reads and preprocesses the input image.
4. Performs forward pass to detect objects.
5. Applies Non-Maximum Suppression to refine detections.
6. Draws bounding boxes and labels for detected objects.
7. Displays the result and saves it as `result.jpg`.

### ▶️ Run Command

```bash
.\Debug\DL.exe ../data/test.jpg
```

Replace `../data/test.jpg` with the path to your own image.

---

## 🧠 Program 2: Face Detection (`DL_face.exe`)

This program uses a ResNet-10 SSD-based face detector. It works on video files, camera streams, or images.

### 🔄 Workflow

1. Loads the face detection model (`.caffemodel`) and its configuration (`.prototxt`).
2. Reads the input source (camera, video, or image).
3. Converts the frame to a 4D blob.
4. Runs a forward pass to detect faces.
5. Draws bounding boxes and confidence values for each detected face.
6. Continuously displays frames until interrupted.

### ▶️ Run Command

```bash
.\Debug\DL_face.exe --model=../data/res10_300x300_ssd_iter_140000.caffemodel --proto=../data/deploy.prototxt.txt
```

You can also add:
- `--video=../data/sample.mp4` to run on a video
- `--camera_device=0` to use the webcam
- `--min_confidence=0.6` to filter weak detections

---

## 📝 Notes

- Both programs rely on OpenCV's DNN module.
- Ensure all required model and configuration files are present in the correct paths.
- Output windows will display the processed frames with bounding boxes and labels.
