cmake_minimum_required(VERSION 3.10)

project(FaceParts)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Tell CMake where to find OpenCV if not in system path
set(OpenCV_DIR "C:/Apps/opencv/build/x64/vc16/lib")

# Requires OpenCV
FIND_PACKAGE( OpenCV 4.0.0 REQUIRED )
MESSAGE("OpenCV version : ${OpenCV_VERSION}")

include_directories(${OpenCV_INCLUDE_DIRS})
link_directories(${OpenCV_LIB_DIR})

ADD_EXECUTABLE( earDetector earDetector.cpp )
TARGET_LINK_LIBRARIES( earDetector ${OpenCV_LIBS} )

ADD_EXECUTABLE( overlayFacemask overlayFacemask.cpp )
TARGET_LINK_LIBRARIES( overlayFacemask ${OpenCV_LIBS} )

ADD_EXECUTABLE( overlayMoustache overlayMoustache.cpp )
TARGET_LINK_LIBRARIES( overlayMoustache ${OpenCV_LIBS} )

ADD_EXECUTABLE( overlayNose overlayNose.cpp )
TARGET_LINK_LIBRARIES( overlayNose ${OpenCV_LIBS} )

ADD_EXECUTABLE( overlaySunglasses overlaySunglasses.cpp )
TARGET_LINK_LIBRARIES( overlaySunglasses ${OpenCV_LIBS} )