cmake_minimum_required(VERSION 3.10)

project(Photo_Tool)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Tell CMake where to find OpenCV if not in system path
set(OpenCV_DIR "C:/Apps/opencv/build/x64/vc16/lib")

# Requires OpenCV
find_package(OpenCV 4.0.0 REQUIRED)
message(STATUS "OpenCV version : ${OpenCV_VERSION}")

include_directories(${OpenCV_INCLUDE_DIRS})
link_directories(${OpenCV_LIB_DIR})

add_executable(${PROJECT_NAME} main.cpp)
target_link_libraries(${PROJECT_NAME} ${OpenCV_LIBS})

add_executable(ch3_sample1 sample1.cpp)
target_link_libraries(ch3_sample1 ${OpenCV_LIBS})

add_executable(ch3_sample2 sample2.cpp)
target_link_libraries(ch3_sample2 ${OpenCV_LIBS})

add_executable(ch3_sample3 sample3.cpp)
target_link_libraries(ch3_sample3 ${OpenCV_LIBS})

add_executable(ch3_sample4 sample4.cpp)
target_link_libraries(ch3_sample4 ${OpenCV_LIBS})

# add_executable(ch3_sample5 sample5.cpp)
# find_package(OpenGL REQUIRED)
# target_link_libraries(ch3_sample5 ${OpenCV_LIBS} OpenGL::GL)


# sample6 requires OpenCV viz module (not built by default)
# add_executable(ch3_sample6 sample6.cpp)
# target_link_libraries(ch3_sample6 ${OpenCV_LIBS})
