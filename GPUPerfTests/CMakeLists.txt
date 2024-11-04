find_package(Vulkan REQUIRED)
find_package(glslang CONFIG)

#message(${CMAKE_BINARY_DIR})
#message(${CMAKE_CURRENT_BINARY_DIR})
#file(GENERATE OUTPUT debug_genexpr CONTENT "$<TARGET_FILE:AssetBinarizer>")

file(GLOB_RECURSE SRCS CONFIGURE_DEPENDS src/*.c src/*.cpp )

file(GLOB SHADER_SRCS CONFIGURE_DEPENDS src/shaders/*.comp)

file(GLOB LANG_SRCS CONFIGURE_DEPENDS src/lang/*.lang)
file(GLOB FONT_SRCS CONFIGURE_DEPENDS font/*.ttf)
file(GLOB ICON_SRCS CONFIGURE_DEPENDS icon/*.png)
file(GLOB TEXT_SRCS CONFIGURE_DEPENDS ../LICENSE ../*.md)

DisableCompilingSpecificSources(${LANG_SRCS})

set(SPV_SHADER_SRCS)
foreach(SHADER_SRC ${SHADER_SRCS})
    cmake_path(GET SHADER_SRC STEM LAST_ONLY ss_stem)
    cmake_path(GET SHADER_SRC PARENT_PATH p_path)

    set(input_filename ${SHADER_SRC})
    set(output_filename ${CMAKE_CURRENT_BINARY_DIR}/shaers/${ss_stem}.spv)

    set(SPV_SHADER_SRCS ${SPV_SHADER_SRCS} ${output_filename})

    add_custom_command(
        COMMENT "Custom Build: glslangValidator"
        OUTPUT ${output_filename}
        DEPENDS ${input_filename}
        COMMAND ${Vulkan_GLSLANG_VALIDATOR_EXECUTABLE}
        ARGS --target-env vulkan1.3 -V ${input_filename} -o ${output_filename}
    )
endforeach()

set(output_filename ${CMAKE_CURRENT_BINARY_DIR}/embedded_resources/ab_embedded_fonts.h)
add_custom_command(
	COMMENT "Custom Build: embeded_fonts"
	OUTPUT ${output_filename}
	DEPENDS ${LANG_SRCS} ${AssetBinarizer}
	COMMAND $<TARGET_FILE:AssetBinarizer>
	ARGS -v -o ${output_filename} ${FONT_SRCS}
)

set(output_filename ${CMAKE_CURRENT_BINARY_DIR}/embedded_resources/ab_embedded_icons.h)
add_custom_command(
	COMMENT "Custom Build: embeded_icons"
	OUTPUT ${output_filename}
	DEPENDS ${LANG_SRCS} ${AssetBinarizer}
	COMMAND $<TARGET_FILE:AssetBinarizer>
	ARGS -v -o ${output_filename} ${ICON_SRCS}
)

set(output_filename ${CMAKE_CURRENT_BINARY_DIR}/embedded_resources/ab_embedded_languages.h)
add_custom_command(
	COMMENT "Custom Build: embedded_languages"
	OUTPUT ${output_filename}
	DEPENDS ${LANG_SRCS} ${AssetBinarizer}
	COMMAND $<TARGET_FILE:AssetBinarizer>
	ARGS -v -o ${output_filename} ${LANG_SRCS}
)

set(output_filename ${CMAKE_CURRENT_BINARY_DIR}/embedded_resources/ab_embedded_shaders.h)
add_custom_command(
	COMMENT "Custom Build: embeded_shaders"
	OUTPUT ${output_filename}
	DEPENDS ${LANG_SRCS} ${AssetBinarizer}
	COMMAND $<TARGET_FILE:AssetBinarizer>
	ARGS -v -o ${output_filename} ${SPV_SHADER_SRCS}
)

set(output_filename ${CMAKE_CURRENT_BINARY_DIR}/embedded_resources/ab_embedded_texts.h)
add_custom_command(
	COMMENT "Custom Build: embded_texts"
	OUTPUT ${output_filename}
	DEPENDS ${LANG_SRCS} ${AssetBinarizer}
	COMMAND $<TARGET_FILE:AssetBinarizer>
	ARGS -v -o ${output_filename} ${TEXT_SRCS}
)


set(EMBED_SRCS 
    ${CMAKE_CURRENT_BINARY_DIR}/embedded_resources/ab_embedded_fonts.h
    ${CMAKE_CURRENT_BINARY_DIR}/embedded_resources/ab_embedded_icons.h
    ${CMAKE_CURRENT_BINARY_DIR}/embedded_resources/ab_embedded_languages.h
    ${CMAKE_CURRENT_BINARY_DIR}/embedded_resources/ab_embedded_shaders.h
    ${CMAKE_CURRENT_BINARY_DIR}/embedded_resources/ab_embedded_texts.h
)

source_group(gen FILES ${SPV_SHADER_SRCS})
source_group(embedded_resources FILES ${EMBED_SRCS})
source_group(TREE ${CMAKE_CURRENT_SOURCE_DIR} FILES ${SRCS} ${LANG_SRCS} ${SHADER_SRCS})

add_executable(${BUILD_TARGET}
        ${SRCS}
        ${SPV_SHADER_SRCS}
        ${EMBED_SRCS}
)

target_compile_definitions(${BUILD_TARGET} PRIVATE
        IMGUI_IMPL_OPENGL_ES3
)

target_include_directories(${BUILD_TARGET} PRIVATE
        include/
        ${Vulkan_INCLUDE_DIRS}
		${CMAKE_CURRENT_BINARY_DIR}/embedded_resources
)

#target_link_libraries(${BUILD_TARGET}
#)