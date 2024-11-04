cmake_minimum_required(VERSION 3.22.1)

if (CMAKE_VERSION VERSION_GREATER 3.12 OR CMAKE_VERSION VERSION_EQUAL 3.12)
  # Enable find_package uses of <PackageName>_ROOT variables.
  cmake_policy(SET CMP0074 NEW)
endif()

ADD_DEFINITIONS(-DUNICODE -D_UNICODE)

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

set(BUILD_ZLIB_EXAMPLES CACHE BOOL OFF)
#FetchContent_Declare(
#    zlib
#    GIT_REPOSITORY https://github.com/madler/zlib.git
#    GIT_TAG        v1.3.1
#)
#FetchContent_MakeAvailable(zlib)
add_subdirectory(Libraries/zlib EXCLUDE_FROM_ALL)

set(ZLIB_ROOT Libraries/zlib)
SET(ZLIB_INCLUDE_DIR ${CMAKE_BINARY_DIR}/Libraries/zlib ${CMAKE_SOURCE_DIR}/Libraries/zlib)
SET(ZLIB_LIBRARY zlib CACHE STRING "zlib library name")

set(BUILD_EXAMPLES OFF)
#FetchContent_Declare(
#    libspng
#    GIT_REPOSITORY https://github.com/randy408/libspng
#    GIT_TAG        v0.7.4
#)
#FetchContent_MakeAvailable(libspng)
add_subdirectory(Libraries/libspng EXCLUDE_FROM_ALL)

include_directories(Libraries/libspng/spng)

set(BUILD_TARGETS AssetBinarizer GPUPerfTests)

foreach (BUILD_TARGET ${BUILD_TARGETS})
   string(STRIP ${BUILD_TARGET} BUILD_TARGET)
    message("Adding ${BUILD_TARGET}...")
    add_subdirectory(${BUILD_TARGET})
endforeach (BUILD_TARGET)

add_dependencies(GPUPerfTests AssetBinarizer)
