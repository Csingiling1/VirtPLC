cmake_minimum_required(VERSION 3.20)
project(OPCUAClient)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find open62541
find_package(open62541 REQUIRED)

# Plugin source files
set(SOURCES
    Source/OPCUAClient/Private/OPCUAClientModule.cpp
    Source/OPCUAClient/Private/OPCUAManager.cpp
)

set(HEADERS
    Source/OPCUAClient/Public/OPCUAClientModule.h
    Source/OPCUAClient/Public/OPCUAManager.h
)

# Create library
add_library(${PROJECT_NAME} SHARED ${SOURCES} ${HEADERS})

# Include directories
target_include_directories(${PROJECT_NAME}
    PUBLIC
        Source/OPCUAClient/Public
    PRIVATE
        Source/OPCUAClient/Private
)

# Link open62541
target_link_libraries(${PROJECT_NAME}
    PRIVATE
        open62541::open62541
)

# Platform-specific settings
if(WIN32)
    target_link_libraries(${PROJECT_NAME} PRIVATE ws2_32)
endif()

# Install rules
install(TARGETS ${PROJECT_NAME}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
