########################################################
# @author Licheng Zhang
# modified on 20210818 for ROOT Feature.
########################################################

CMAKE_MINIMUM_REQUIRED(VERSION 3.3 FATAL_ERROR)
########################################################

PROJECT(Full_SIM)

if(NOT TARGET Garfield)
  find_package(Garfield REQUIRED)
endif()
find_package(ROOT REQUIRED)

# ROOT version 6 required
if(ROOT_FOUND)
  STRING(REGEX MATCH "6.*" VERSION6MATCH ${ROOT_VERSION})
  if(NOT VERSION6MATCH)
    message(FATAL_ERROR "requires ROOT 6")
  endif()
endif()

# Include ROOT's CMake functions for dictionary generation
# include("${ROOT_DIR}/modules/RootNewMacros.cmake")
include("${ROOT_DIR}/ROOTUseFile.cmake")

include_directories(${PROJECT_SOURCE_DIR}
                    ${PROJECT_SOURCE_DIR}/include
                    ${PROJECT_SOURCE_DIR}/src
                    ${ROOT_INCLUDE_DIRS})
                    
file(GLOB sources ${PROJECT_SOURCE_DIR}/src/*.cc)
file(GLOB headers ${PROJECT_SOURCE_DIR}/include/*.hh)

#### AnalyticField         #############################

add_executable(Full_SIM.exe Full_SIM.cc ${sources} ${headers})
target_link_libraries(Full_SIM.exe Garfield ${ROOT_LIBRARIES})