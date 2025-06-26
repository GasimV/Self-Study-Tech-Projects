cmake_minimum_required(VERSION 3.10)

project(ObjClass)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Set OpenCV path (adjust if installed elsewhere)
set(OpenCV_DIR "C:/Apps/opencv/build/x64/vc16/lib")

# Find OpenCV
find_package(OpenCV REQUIRED)
message("OpenCV version: ${OpenCV_VERSION}")

include_directories(${OpenCV_INCLUDE_DIRS})
link_directories(${OpenCV_LIB_DIR})

ADD_EXECUTABLE( ${PROJECT_NAME} main.cpp utils/MultipleImageWindow.cpp)
TARGET_LINK_LIBRARIES( ${PROJECT_NAME} ${OpenCV_LIBS} )