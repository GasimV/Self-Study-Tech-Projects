# Object Tracking Algorithms with OpenCV

This suite consists of multiple tracking programs demonstrating classical computer vision algorithms for real-time video tracking using OpenCV. Each program launches a specific tracking technique and processes live video from a webcam.

---

## 🎯 Programs and Commands

### 1. CAMShift Tracker
Tracks a user-selected object using the CAMShift algorithm based on color histogram backprojection.

```bash
.\Debug\camshiftTracker.exe
```

- Select an ROI with the mouse.
- The tracker will follow the object using adaptive meanshift tracking.

---

### 2. Color-Based Object Tracker
Detects and tracks objects based on specific color ranges in HSV color space (e.g., blue).

```bash
.\Debug\coloredObjectTracker.exe
```

- Converts webcam feed to HSV.
- Segments and tracks the defined color (blue in current setup).

---

### 3. Harris Corner Tracker
Detects and marks corners in video frames using the Harris corner detection method.

```bash
.\Debug\harrisCornersTracker.exe 10
```

- Argument: Harris detector block size.
- Displays corners detected in real time.

---

### 4. Lucas-Kanade Optical Flow Tracker
Tracks points selected by mouse using the Lucas-Kanade optical flow algorithm.

```bash
.\Debug\lucasKanadeTracker.exe
```

- Click to select tracking points.
- Tracks features across frames using pyramidal Lucas-Kanade method.

---

### 5. Farneback Optical Flow
Visualizes dense optical flow using the Farneback algorithm.

```bash
.\Debug\farnebackTracker.exe
```

- Shows motion vectors across the frame using grid-based visualization.

---

### 6. Good Features to Track
Detects and displays top N features using the Shi-Tomasi method.

```bash
.\Debug\goodFeaturesToTrack.exe 10
```

- Argument: Number of corners to detect.
- Highlights good feature points for tracking in the webcam stream.

---

## 📝 Notes

- All programs use a live webcam feed.
- Press `ESC` to exit any running application.
- Ideal for comparing classical computer vision tracking algorithms.
