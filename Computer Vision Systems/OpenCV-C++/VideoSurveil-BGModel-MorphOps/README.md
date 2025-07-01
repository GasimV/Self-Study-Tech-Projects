# Video Surveillance, Background Modeling, and Morphological Operations

This project demonstrates basic computer vision operations using OpenCV 4.11.0, including:

- Frame Differencing
- Background Subtraction
- Morphological Operations: Dilation, Erosion, Opening, Closing, Gradient, Top Hat, Black Hat

## Setup Steps

## Building the Project

In your project directory:

```bash
mkdir build
cd build
cmake ..
cmake --build .
```

## Executing the Programs

Each executable supports the following command-line usage:

### Frame Differencing (Webcam-based motion detection)
```bash
.\Debug\frameDifferencing.exe
```

### Background Subtraction (Webcam)
```bash
.\Debug\backgroundSubtraction.exe
```

### Morphological Operations (on static image)
```bash
.\Debug\morphologicalOperations.exe ../resources/test.png 5
```

### Dilation
```bash
.\Debug\dilation.exe ../resources/test.png 5
```

### Erosion
```bash
.\Debug\erosion.exe ../resources/test.png 5
```