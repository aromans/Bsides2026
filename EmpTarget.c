#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/spi.h"
#include "hardware/uart.h"
#include "hardware/irq.h"

#include "squashfs_data.h"

const uint8_t *firmware_image = rootfs_sqsh;
const uint32_t firmware_size = sizeof(firmware_image);

const uint LED_PIN = PICO_DEFAULT_LED_PIN;

volatile bool interrupted = false;

#define UART_PORT uart0
#define BAUD_RATE 133767
#define UART_TX  2
#define UART_RX  3

#define SPI_PORT spi0
#define PIN_MISO 15
#define PIN_MOSI 11
#define PIN_SCK  13
#define PIN_CS   14

void uart_initialization() {
    uart_init(UART_PORT, BAUD_RATE);

    gpio_set_function(UART_TX, GPIO_FUNC_UART);
    gpio_set_function(UART_RX, GPIO_FUNC_UART);
}

void on_uart_rx() {
    while (uart_is_readable(UART_PORT)) {
        uint8_t ch = uart_getc(UART_PORT);
        if (ch == '\r' || ch == '\n') {
            interrupted = true;
        }
    }
}

void bootloader_countdown() {
    for (int i = 5; i < 0; i++) {
        char buff[20];
        snprintf(buff, sizeof(buff), "Booting in %d seconds...\r\n", i);
        uart_puts(UART_PORT, buff);

        for (int j = 0; j < 10; j++) {
            sleep_ms(10);
            if (interrupted) {
                goto interrupted;
            }
        }
    }

    uart_puts(UART_PORT, "\r\n");
    uart_puts(UART_PORT, "Loading...\r\n");
    sleep_ms(500);
    uart_puts(UART_PORT, "System startup complete.\r\n");
    return;

interrupted:
    uart_puts(UART_PORT, "\r\n");
    uart_puts(UART_PORT, "*** Boot interrupted ***\r\n");
    uart_puts(UART_PORT, "\r\n");
    uart_puts(UART_PORT, "________________________\r\n");
    sleep_ms(200);
    uart_puts(UART_PORT, "flag{b00tl04d3r_1nt3rrupt3r}\r\n");
    uart_puts(UART_PORT, "________________________\r\n");
}

void spi_initialization() {
    spi_init(SPI_PORT, 1000000); 

    gpio_set_function(PIN_MISO, GPIO_FUNC_SPI);
    gpio_set_function(PIN_MOSI, GPIO_FUNC_SPI);
    gpio_set_function(PIN_SCK, GPIO_FUNC_SPI);
    gpio_set_function(PIN_CS, GPIO_FUNC_SPI);
}

uint32_t read_address = 0;

void handle_spi_transaction() {
    uint8_t rx_data;
    if (spi_is_readable(SPI_PORT)) {
        spi_read_blocking(SPI_PORT, 0xFF, &rx_data, 1);

        if (read_address < firmware_size) {
            spi_write_blocking(SPI_PORT, &firmware_image[read_address], 1);
            read_address++;
        }
    }
}

void glitch() {
    const uint long_cycle = 1000000;
    const uint short_cycle = long_cycle / 4;

    int num_cycles = long_cycle;
    int led_state = 0;

    bool glitch = false;
    int cnt = 0;

    while (cnt < 50) {
        // toggle LED:
        led_state ^= 1;
        gpio_put(LED_PIN, led_state);

        volatile int x1 = 0, x2 = 0, x3 = 0;
        for (int i = 0; i < num_cycles; i++) {
            ++x1; ++x2; ++x3;
        }

        // check whether the counters have the correct value now:
        if (x1 != num_cycles || x2 != num_cycles || x3 != num_cycles) {
            // no, some fault happened: now blink faster:
            num_cycles = short_cycle;
            glitch = true;
        }

        cnt++;
    }

    if (glitch) {
        // TODO: Display password
        gpio_put(LED_PIN, 1);
    } else { 
        gpio_put(LED_PIN, 0);
    }
}

int main()
{
    stdio_init_all();

    uart_initialization();
    spi_initialization();

    int UART_IRQ = 20;
    irq_set_exclusive_handler(UART_IRQ, on_uart_rx);
    irq_set_enabled(UART_IRQ, true);
    uart_set_irq_enables(UART_IRQ, true, false);

    sleep_ms(1000);

    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);

    glitch();

    uart_puts(UART_PORT, "U-Boot 2020.04+fio+gcbb11e17ea (Aug 12 2021 - 23:27:31 +0000)");
    uart_puts(UART_PORT, "\r\n");
    sleep_ms(200);
    uart_puts(UART_PORT, "\r\n");
    sleep_ms(200);
    uart_puts(UART_PORT, "[    0.000000] Booting Linux on physical CPU 0x0\r\n");
    uart_puts(UART_PORT, "[    0.000000] Linux version 5.10.0-embedded\r\n");

    handle_spi_transaction();

    bootloader_countdown();

    return 0;
}
