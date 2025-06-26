cmake_minimum_required(VERSION 3.10)

project(ObjDetect)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Set OpenCV path (adjust if installed elsewhere)
set(OpenCV_DIR "C:/Apps/opencv/build/x64/vc16/lib")

# Find OpenCV
find_package(OpenCV REQUIRED)
message("OpenCV version: ${OpenCV_VERSION}")

include_directories(${OpenCV_INCLUDE_DIRS})
link_directories(${OpenCV_LIB_DIR})

ADD_EXECUTABLE(camshiftTracker  camshiftTracker.cpp )
TARGET_LINK_LIBRARIES( camshiftTracker ${OpenCV_LIBS} )

ADD_EXECUTABLE( coloredObjectTracker coloredObjectTracker.cpp )
TARGET_LINK_LIBRARIES( coloredObjectTracker ${OpenCV_LIBS} )

ADD_EXECUTABLE( farnebackTracker  farnebackTracker.cpp )
TARGET_LINK_LIBRARIES( farnebackTracker ${OpenCV_LIBS} )

ADD_EXECUTABLE( goodFeaturesToTrack goodFeaturesToTrack.cpp )
TARGET_LINK_LIBRARIES( goodFeaturesToTrack ${OpenCV_LIBS} )

ADD_EXECUTABLE( harrisCornersTracker harrisCornersTracker.cpp )
TARGET_LINK_LIBRARIES( harrisCornersTracker ${OpenCV_LIBS} )

ADD_EXECUTABLE( lucasKanadeTracker lucasKanadeTracker.cpp )
TARGET_LINK_LIBRARIES( lucasKanadeTracker ${OpenCV_LIBS} )