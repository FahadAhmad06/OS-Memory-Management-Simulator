cmake_minimum_required(VERSION 3.14)
project(os_memory_simulator_backend VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(nlohmann_json 3.9.0 REQUIRED)

set(BACKEND_SOURCES
    src/allocation/first_fit.cpp
    src/allocation/best_fit.cpp
    src/allocation/worst_fit.cpp
    src/paging/paging.cpp
    src/page_replacement/fifo.cpp
    src/page_replacement/lru.cpp
    src/page_replacement/optimal.cpp
    src/comparison/allocation_comparison.cpp
    src/comparison/page_replacement_comparison.cpp
    src/common/json_handler.cpp
    src/main.cpp
)

add_executable(os_memory_simulator ${BACKEND_SOURCES})

target_include_directories(os_memory_simulator
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_link_libraries(os_memory_simulator
    PRIVATE
        nlohmann_json::nlohmann_json
)
