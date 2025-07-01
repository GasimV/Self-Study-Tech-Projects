# OCR Text Segmentation with OpenCV and Tesseract (Windows)

This project demonstrates how to detect, extract, and deskew text regions from a document image (e.g., tickets or receipts) using OpenCV, and optionally OCR them using Tesseract.

---

## 📦 Environment Setup

### 1. Clone and Bootstrap vcpkg

```bash
cd C:\Apps
git clone https://github.com/Microsoft/vcpkg
cd vcpkg
bootstrap-vcpkg.bat
```

### 2. Install Tesseract for 64-bit Projects

```bash
vcpkg install tesseract:x64-windows
```

> ⚠️ This may take up to 15 minutes depending on your system and internet connection.

---

## 💻 Sample Usage: segment.cpp

- Loads a ticket image `ticket.png`
- Applies Otsu binarization
- Detects rectangular text regions via contour + dilation
- Filters small, square, or irrelevant contours
- Deskews and crops each text region
- Displays each cropped text in a popup window

> Note: Output is not saved to files — you can extend this with `imwrite()`.

---

## 📝 Tip for VS Code Users

Update `c_cpp_properties.json`:

```json
{
  "configurations": [
    {
      "name": "Win32",
      "includePath": [
        "${workspaceFolder}/**",
        "C:/Apps/opencv/build/include",
        "C:/Apps/opencv/build/include/opencv2",
        "C:/Apps/vcpkg/installed/x64-windows/include"
      ],
      "defines": [],
      "compilerPath": "C:/msys64/ucrt64/bin/g++.exe", // Adjust to your MSYS2 path
      "cStandard": "c11",
      "cppStandard": "c++17",
      "intelliSenseMode": "windows-gcc-x64"
    }
  ],
  "version": 4
}
```

---

## ✅ Result

When run with a valid `ticket.png` image, each detected text region appears in a separate popup window, correctly rotated and bordered.

---
---

## 💻 Additional Sample Usage

### 📎 segmentOcr.exe
Runs text segmentation with OCR output to file using Tesseract.

```bash
.\Debug\segmentOcr.exe
```

**Workflow:**
- Loads `ticketHigh.png` and binarizes it.
- Segments text regions via dilation and contour filtering.
- Deskews and crops each region.
- Uses Tesseract OCR (`por` language) to extract text.
- Outputs results into `ticket.txt`.

---

### 📎 segment.exe
Runs text segmentation and displays each detected region.

```bash
.\Debug\segment.exe
```

**Workflow:**
- Loads `ticket.png`, binarizes it with Otsu.
- Extracts text regions using contour and geometric filtering.
- Deskews and crops each detected region.
- Displays the output as popup windows.

---

### 📎 segmentOcrHigh.exe
Performs OCR on high-resolution segmented text images.

```bash
.\Debug\segmentOcrHigh.exe
```

**Workflow:**
- Similar to `segmentOcr.exe` but uses stricter thresholds and padding.
- Ideal for cleaner OCR on higher-resolution documents.
- Outputs recognized text to `ticket.txt`.

