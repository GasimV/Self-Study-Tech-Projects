# FaceParts-MaskOverlay

This project demonstrates face and facial part detection using Haar cascades with OpenCV, and overlays images such as masks, glasses, noses, and moustaches.

## Build Instructions

```bash
mkdir build
cd build
cmake ..
cmake --build .
```

## Executables and Usage

### ✅ Overlay Face Mask
```bash
./Debug/overlayFacemask.exe ../resources/haarcascade_frontalface_alt.xml ../resources/mask.jpg
```

### ✅ Overlay Sunglasses
```bash
./Debug/overlaySunglasses.exe ../resources/haarcascade_frontalface_alt.xml ../resources/haarcascade_eye.xml ../resources/glasses.jpg
```

### ✅ Overlay Nose
```bash
./Debug/overlayNose.exe ../resources/haarcascade_frontalface_alt.xml ../resources/haarcascade_mcs_nose.xml ../resources/nose.png
```

### ✅ Overlay Moustache
```bash
./Debug/overlayMoustache.exe ../resources/haarcascade_frontalface_alt.xml ../resources/haarcascade_mcs_nose.xml ../resources/moustache.png
```

### ✅ Ear Detector
```bash
./Debug/earDetector.exe ../resources/haarcascade_frontalface_alt.xml ../resources/haarcascade_mcs_rightear.xml ../resources/haarcascade_mcs_leftear.xml
```

## Required Resources

Ensure the following files exist in your `resources/` directory:

- `haarcascade_frontalface_alt.xml`
- `haarcascade_eye.xml`
- `haarcascade_mcs_nose.xml`
- `haarcascade_mcs_rightear.xml`
- `haarcascade_mcs_leftear.xml`
- `mask.jpg`
- `glasses.jpg`
- `moustache.png`
- `nose.png`
