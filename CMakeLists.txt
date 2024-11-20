cmake_minimum_required(VERSION 3.22.1)

set(CMAKE_PROJECT_TOP_LEVEL_INCLUDES cmake/conan_provider.cmake)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if (CMAKE_VERSION VERSION_GREATER 3.12 OR CMAKE_VERSION VERSION_EQUAL 3.12)
  # Enable find_package uses of <PackageName>_ROOT variables.
  cmake_policy(SET CMP0074 NEW)
endif()

if(WIN32)
   set(OUTPUT_BINARY_DIR ${CMAKE_BINARY_DIR})
else(WIN32)
   set(OUTPUT_BINARY_DIR ${CMAKE_BINARY_DIR}/bin)
endif()

message("OUTPUT_BINARY_DIR = ${OUTPUT_BINARY_DIR}")

add_compile_definitions(UNICODE _UNICODE)
#add_compile_definitions(_DEBUG)


function (DisableCompilingSpecificSources)
   set(options OPTIONAL)
   set(oneValueArgs ONE_TARGET)
   set(multiValueArgs TARGETS)
   cmake_parse_arguments(PARSE_ARGV 0 arg "${options}" "${oneValuArgs}" "${multiValueArgs}")

   foreach(file ${TARGETS})
    set_source_files_properties( ${file} PROPERTIES HEADER_FILE_ONLY TRUE )
   endforeach()
endfunction()

function(add_executable)
   string(TOUPPER ${ARGV1} argv1_upper)
   #message(${ARGV}, ${argv1_upper})
   #set(CMAKE_PDB_OUTPUT_DIRECTORY ${OUTPUT_BINARY_DIR})
   #set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${OUTPUT_BINARY_DIR})
   _add_executable(${ARGV})
   if (NOT ${argv1_upper} STREQUAL IMPORTED)
      add_custom_command(
         TARGET ${ARGV0}
         POST_BUILD
         COMMAND ${CMAKE_COMMAND} -E make_directory ${OUTPUT_BINARY_DIR}/$<CONFIGURATION>/
         COMMAND ${CMAKE_COMMAND} -E copy_if_different $<TARGET_FILE:${ARGV0}> ${OUTPUT_BINARY_DIR}/$<CONFIGURATION>
      )
   endif()
endfunction()

function(add_library)
   string(TOUPPER ${ARGV1} argv1_upper)
   if (${ARGC} GREATER 2)
      string(TOUPPER ${ARGV2} argv2_upper)
   endif()

   #set(CMAKE_PDB_OUTPUT_DIRECTORY ${OUTPUT_BINARY_DIR})
   #set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${OUTPUT_BINARY_DIR})
   _add_library(${ARGV})
   #message(${ARGV}, ${argv1_upper}, ${argv2_upper})
   if (${argv1_upper} STREQUAL SHARED OR ${argv1_upper} STREQUAL STATIC)
      if ((${ARGC} LESS 3 OR NOT ${argv2_upper} STREQUAL IMPORTED))
         set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${OUTPUT_BINARY_DIR})
         add_custom_command(
               TARGET ${ARGV0}
               POST_BUILD
               COMMAND ${CMAKE_COMMAND} -E make_directory ${OUTPUT_BINARY_DIR}/$<CONFIGURATION>/
               COMMAND ${CMAKE_COMMAND} -E copy_if_different $<TARGET_FILE:${ARGV0}> ${OUTPUT_BINARY_DIR}/$<CONFIGURATION>/
               DEPENDS $<TARGET_OBJECTS:${ARGV0}>
         )
      endif()
   endif()
   #_add_library(${ARGV})
endfunction()

project("gpuperftests" C CXX)

find_package(Vulkan REQUIRED)
set(ZLIB_USE_STATIC_LIBS ON)
find_package(ZLIB REQUIRED)
#find_package(SPNG REQUIRED)

include_directories(Libraries)

add_subdirectory(Libraries/libspng EXCLUDE_FROM_ALL)
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
