cmake_minimum_required(VERSION 3.10)

project(Chapter2)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Tell CMake where to find OpenCV if not in system path
set(OpenCV_DIR "C:/Apps/opencv/build/x64/vc16/lib")

find_package(OpenCV REQUIRED)

message(STATUS "OpenCV version : ${OpenCV_VERSION}")

# Add all executables
add_executable(sample1 sample1.cpp)
target_link_libraries(sample1 ${OpenCV_LIBS})

add_executable(sample2 sample2.cpp)
target_link_libraries(sample2 ${OpenCV_LIBS})

add_executable(sample3 sample3.cpp)
target_link_libraries(sample3 ${OpenCV_LIBS})

add_executable(${PROJECT_NAME} main.cpp)
target_link_libraries(${PROJECT_NAME} ${OpenCV_LIBS})
