#include <iostream>
#include <string>
#include <sstream>
#include <filesystem> // C++17 feature
using namespace std;
namespace fs = std::filesystem;

// OpenCV includes
#include "opencv2/core.hpp"
#include "opencv2/highgui.hpp"
#include "opencv2/videoio.hpp"
using namespace cv;

// Command line keys
const char* keys =
{
    "{help h usage ? | | print this message}"
    "{@video | | Video file, if not defined, fallback to webcam}"
};

int main(int argc, const char** argv)
{
    CommandLineParser parser(argc, argv, keys);
    parser.about("Chapter 2. v1.0.0");

    if (parser.has("help")) {
        parser.printMessage();
        return 0;
    }

    String videoFile = parser.get<String>(0);
    if (!parser.check()) {
        parser.printErrors();
        return 0;
    }

    VideoCapture cap;

    if (!videoFile.empty() && fs::exists(videoFile)) {
        cout << "📼 Opening video file: " << videoFile << endl;
        cap.open(videoFile);
    } else {
        cout << "🎥 Video file not provided or not found. Trying webcam..." << endl;
        cap.open(0); // Try default webcam
    }

    if (!cap.isOpened()) {
        cerr << "❌ Failed to open video source (neither file nor webcam)." << endl;
        return -1;
    }

    namedWindow("Video", 1);
    for (;;) {
        Mat frame;
        cap >> frame;
        if (frame.empty()) break;

        imshow("Video", frame);
        if (waitKey(30) >= 0) break;
    }

    cap.release();
    return 0;
}
