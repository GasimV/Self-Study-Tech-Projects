cmake_minimum_required(VERSION 3.10)

project(DL)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Set OpenCV path (adjust if installed elsewhere)
set(OpenCV_DIR "C:/Apps/opencv/build/x64/vc16/lib")

# Find OpenCV
find_package(OpenCV REQUIRED)
message("OpenCV version: ${OpenCV_VERSION}")

# Main executable
add_executable(${PROJECT_NAME} main.cpp)
target_link_libraries(${PROJECT_NAME} ${OpenCV_LIBS})

# Face detection executable
add_executable(${PROJECT_NAME}_face resnet_ssd_face.cpp)
target_link_libraries(${PROJECT_NAME}_face ${OpenCV_LIBS})