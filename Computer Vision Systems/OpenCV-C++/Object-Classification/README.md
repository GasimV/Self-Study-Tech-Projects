# Object Classification with OpenCV

This program performs simple image classification based on shape characteristics using OpenCV. It visualizes intermediate steps like preprocessing and contour detection using a multi-image canvas.

## How to Run

### Command

```bash
.\Debug\ObjClass.exe ../data/test.pgm
```

Replace `test.pgm` with the path to any compatible image you want to classify.

### Description

This executable accepts a grayscale image and classifies objects in the image using simple geometric features. The results are shown in a custom OpenCV multi-view GUI (`MultipleImageWindow`) where you can see:

- The original input image.
- Intermediate processing steps.
- The final classification results.

## Requirements

- The image should be in grayscale (PGM or converted format).
- OpenCV must be properly linked with GUI (highgui) modules.