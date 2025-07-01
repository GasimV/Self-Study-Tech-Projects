cmake_minimum_required(VERSION 3.10)

# ✅ vcpkg toolchain must be before project()
set(CMAKE_TOOLCHAIN_FILE "C:/Apps/vcpkg/scripts/buildsystems/vcpkg.cmake" CACHE STRING "")

project(OCRSegmentation)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ✅ OpenCV will be resolved by vcpkg — no need to set OpenCV_DIR manually
# Comment or remove the line below
# set(OpenCV_DIR "C:/Apps/opencv/build/x64/vc16/lib")

# ✅ Find dependencies
find_package(OpenCV REQUIRED)
find_package(Tesseract CONFIG REQUIRED)

message("OpenCV version: ${OpenCV_VERSION}")

# ✅ Executables
add_executable(segment segment.cpp)
add_executable(segmentOcr segmentOcr.cpp)
add_executable(segmentOcrHigh segmentOcrHigh.cpp)

# ✅ Link libraries
target_link_libraries(segment ${OpenCV_LIBS})
target_link_libraries(segmentOcr ${OpenCV_LIBS} Tesseract::libtesseract)
target_link_libraries(segmentOcrHigh ${OpenCV_LIBS} Tesseract::libtesseract)
