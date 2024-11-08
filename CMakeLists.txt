cmake_minimum_required(VERSION 3.22.1)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if (CMAKE_VERSION VERSION_GREATER 3.12 OR CMAKE_VERSION VERSION_EQUAL 3.12)
  # Enable find_package uses of <PackageName>_ROOT variables.
  cmake_policy(SET CMP0074 NEW)
endif()

add_compile_definitions(-DUNICODE -D_UNICODE)

include(FetchContent)

function (DisableCompilingSpecificSources)
   set(options OPTIONAL)
   set(oneValueArgs ONE_TARGET)
   set(multiValueArgs TARGETS)
   cmake_parse_arguments(PARSE_ARGV 0 arg "${options}" "${oneValuArgs}" "${multiValueArgs}")

   foreach(file ${TARGETS})
    set_source_files_properties( ${file} PROPERTIES HEADER_FILE_ONLY TRUE )
   endforeach()
endfunction()

project("gpuperftests" C CXX)

find_package(Vulkan REQUIRED)

include_directories(Libraries)

set(ZLIB_BUILD_EXAMPLES OFF CACHE BOOL "Enable Zlib Examples")
add_subdirectory(Libraries/zlib )

set(ZLIB_ROOT Libraries/zlib)
SET(ZLIB_INCLUDE_DIR ${CMAKE_BINARY_DIR}/Libraries/zlib ${CMAKE_SOURCE_DIR}/Libraries/zlib)
#SET(ZLIB_LIBRARY zlib)# CACHE STRING "zlib library name")

set(BUILD_EXAMPLES OFF CACHE BOOL "Build examples" )
set(SPNG_SHARED OFF CACHE BOOL "Build shared libs" )

add_subdirectory(Libraries/libspng EXCLUDE_FROM_ALL)
include_directories(Libraries/libspng/spng)

add_subdirectory(Libraries/SDL EXCLUDE_FROM_ALL)


include_directories(Libraries/imgui)
include_directories(Libraries/imgui/backends)
include_directories(Libraries/imgui/misc/freetype)

add_subdirectory(Libraries/ImGuiFileDialog EXCLUDE_FROM_ALL)
include_directories(Libraries/ImGuiFileDialog)

set(USE_GLFW OFF CACHE BOOL "Use GLFW" FORCE)

if (USE_GLFW)
   add_compile_definitions(-DUSE_GLFW)
endif()

set(BUILD_TARGETS AssetBinarizer GPUPerfTests)

foreach (BUILD_TARGET ${BUILD_TARGETS})
   string(STRIP ${BUILD_TARGET} BUILD_TARGET)
    message("Adding ${BUILD_TARGET}...")
    add_subdirectory(${BUILD_TARGET})
endforeach (BUILD_TARGET)

add_dependencies(GPUPerfTests AssetBinarizer)
