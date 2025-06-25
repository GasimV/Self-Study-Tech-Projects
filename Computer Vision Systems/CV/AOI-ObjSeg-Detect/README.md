# AOI-ObjSeg-Detect

**Automated Optical Inspection, Object Segmentation, and Detection**

This project demonstrates background correction and object segmentation using OpenCV. It is built with CMake and Visual Studio on Windows, leveraging OpenCV 4.x functionality.

## 📁 Folder Structure

```
AOI-ObjSeg-Detect/
│
├── build/                  # Build directory (created after configuration)
├── data/                   # Contains sample images (e.g., test_noise.pgm, light.pgm)
├── utils/
│   ├── MultipleImageWindow.cpp
│   └── MultipleImageWindow.h
├── main.cpp                # Main application
├── CMakeLists.txt          # Build configuration
└── README.md               # This documentation
```

## ⚙️ Requirements

- Visual Studio 2022 (or later)
- CMake 3.10+
- OpenCV 4.x installed locally (path set in CMake)
- Windows SDK (e.g., 10.0.22000.0)

## 🧱 Build Instructions

From PowerShell:

```powershell
cd C:\AOI-ObjSeg-Detect
mkdir build
cd build
cmake ..
cmake --build .
```

This will create the executable at:

```
.\build\Debug\Chapter5.exe
```

## 🧪 Example Usage

To run the executable with different background correction modes:

```powershell
.\Debug\Chapter5.exe ..\data\test_noise.pgm ..\data\light.pgm --lightMethod=2
```

You will see output such as:
```
Number of objects detected: 19
```

### 🧩 Light Removal Methods

| Option         | Value | Description                       |
|----------------|-------|-----------------------------------|
| `--lightMethod`| `0`   | Difference image                  |
|                | `1`   | Division (normalization)          |
|                | `2`   | No light correction               |

### 🔍 Segmentation Methods

| Option        | Value | Description                           |
|---------------|-------|---------------------------------------|
| `--segMethod` | `1`   | Connected Components                  |
|               | `2`   | Connected Components with Stats       |
|               | `3`   | Find Contours                         |

## 🆘 Help Command

Run to see usage options:

```powershell
.\Debug\Chapter5.exe --help
```

## ⚠️ Notes

- Some OpenCV GTK/Qt-related `.dll` loading warnings are normal and can be ignored if you're using the WIN32 backend.
- Type conversion warnings (C4267, C4244) in `MultipleImageWindow.cpp` are harmless, but you may silence them with explicit casts if desired.


Each run shows a GUI window with segmented or processed output based on the chosen method.
