# Generated Cmake Pico project file

cmake_minimum_required(VERSION 3.12)

# == DO NOT EDIT THE FOLLOWING LINES for the Raspberry Pi Pico VS Code Extension to work ==
if(WIN32)
    set(USERHOME $ENV{USERPROFILE})
else()
    set(USERHOME $ENV{HOME})
endif()
set(sdkVersion 2.2.0)
set(toolchainVersion 13_2_Rel1)
set(picotoolVersion 2.2.0-a4)
set(picoVscode ${USERHOME}/.pico-sdk/cmake/pico-vscode.cmake)
if (EXISTS ${picoVscode})
    include(${picoVscode})
endif()
# ====================================================================================

include(pico_sdk_import.cmake)

project(EmpTarget VERSION 1.0.0)

add_executable(EmpTarget EmpTarget.c)

target_link_libraries(EmpTarget
        pico_stdlib
        hardware_spi
        hardware_uart
        hardware_irq)

pico_sdk_init()

pico_enable_stdio_usb(EmpTarget 1)
pico_enable_stdio_uart(EmpTarget 0)

pico_add_extra_outputs(EmpTarget)
