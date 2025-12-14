file(GLOB_RECURSE SOURCES "*.cpp" "*.hpp")
list(FILTER SOURCES EXCLUDE REGEX ".*/test/.*")
list(FILTER SOURCES EXCLUDE REGEX ".*/test/.*")
list(FILTER SOURCES EXCLUDE REGEX ".*/tinyxml2-11.0.0/xmltest.cpp$")
list(FILTER SOURCES EXCLUDE REGEX ".*/tinyxml2-11.0.0/contrib/html5-printer.cpp$")
set(INFERENCE_MODULE_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../scl-machine/problem-solver/cxx/inferenceModule")
add_library(segmentInCircumferenceModule SHARED ${SOURCES})

target_include_directories(segmentInCircumferenceModule
        PRIVATE
        ${CMAKE_CURRENT_LIST_DIR}
        ${SC_MEMORY_SRC}
        ${SC_KPM_SRC}
        ${SC_BUILDER_SRC}/src
        ${INFERENCE_MODULE_DIR}          # Основные заголовки
        ${INFERENCE_GENERATED_DIR}       # Сгенерированные файлы
        ${CMAKE_CURRENT_LIST_DIR}/generated
        ${CMAKE_CURRENT_LIST_DIR}/lib/tinyxml22-11.0.0

)

target_link_libraries(segmentInCircumferenceModule
        PRIVATE
        sc-memory
        sc-agents-common
        sc-builder-lib
        inferenceModule
)
add_dependencies(segmentInCircumferenceModule inferenceModule)

sc_codegen_ex(segmentInCircumferenceModule ${CMAKE_CURRENT_LIST_DIR} ${CMAKE_CURRENT_LIST_DIR}/generated)