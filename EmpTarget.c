#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/spi.h"
#include "hardware/uart.h"
#include "hardware/irq.h"

#include "squashfs_data.h"

const uint8_t *firmware_image = rootfs_sqsh;

const uint LED_PIN = PICO_DEFAULT_LED_PIN;

volatile bool interrupted = false;

#define UART_ID uart1
#define BAUD_RATE 115200
#define UART_TX  4
#define UART_RX  5

#define SPI_PORT spi0
#define PIN_MISO 16
#define PIN_MOSI 19
#define PIN_SCK  18
#define PIN_CS   17

void uart_initialization() {
    uart_init(UART_ID, BAUD_RATE);
    gpio_set_function(UART_TX, GPIO_FUNC_UART); //TX
    gpio_set_function(UART_RX, GPIO_FUNC_UART); //RX
}

void on_uart_rx() {
    while (uart_is_readable(UART_ID)) {
        uint8_t ch = uart_getc(UART_ID);
        if (ch == '\r' || ch == '\n') {
            interrupted = true;
        }
    }
}

void bootloader_countdown() {
    for (int i = 5; i >= 0; i--) {
        char buff[35];
        snprintf(buff, sizeof(buff), "Hit any key to stop autoboot: %d\r", i);
        uart_puts(UART_ID, buff);

        for (int j = 0; j < 10; j++) {
            sleep_ms(100);
            if (interrupted) {
                goto interrupted;
            }
        }
    }

    uart_puts(UART_ID, "\r\n");
    uart_puts(UART_ID, "Loading...\r\n");
    sleep_ms(500);
    uart_puts(UART_ID, "System startup complete.\r\n");
    return;

interrupted:
    uart_puts(UART_ID, "\r\n");
    uart_puts(UART_ID, "*** Boot interrupted ***\r\n");
    uart_puts(UART_ID, "\r\n");
    uart_puts(UART_ID, "________________________\r\n");
    sleep_ms(200);
    uart_puts(UART_ID, "flag{b00tl04d3r_1nt3rrupt3r}\r\n");
    uart_puts(UART_ID, "________________________\r\n");
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
    while (read_address < rootfs_sqsh_len) {
        spi_read_blocking(SPI_PORT, 0xFF, &rx_data, 1);
        spi_write_blocking(SPI_PORT, &firmware_image[read_address], 1);
        read_address++;
    }
}

void xor_decrypt(const uint8_t* encrypted, char* output, int len) {
    uint32_t key;
    uint8_t* key_bytes;
    int i;

    key = 0xdeadbeef;
    key_bytes = (uint8_t*)&key;

    for (i = 0; i < len; i++) {
        output[i] = encrypted[i] ^ key_bytes[i % 4];
    }
    output[len] = '\0';
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
        const uint8_t encrypted_password[] = {
            0x8a,0xd2,0x9e,0xbd,0x9b,0xcc,0x9d,
            0xb3,0xdb,0xd9,0xc3,0xbb,0x9b,0xd7,
            0xce,0x81,0x9f,0xcb,0xc1,0xeb,0x8a,
            0xcd,0xf2,0xb8,0xdf,0xcc,0xf2,0xb8,
            0x9a,0xd0,0xf2,0xea,0x81,0xda,0xf2,
            0xae,0x9d,0x8e,0xcb,0xef,0x9b
        };

        char password[42];
        xor_decrypt(encrypted_password, password, sizeof(encrypted_password));
        printf("Password: %s\n", password);
        gpio_put(LED_PIN, 1);
    } else {
        gpio_put(LED_PIN, 0);
    }
}

int main()
{
    stdio_init_all();

    printf("Hello, world!");

    uart_initialization();
    spi_initialization();

    int UART_IRQ = UART1_IRQ;
    irq_set_exclusive_handler(UART_IRQ, on_uart_rx);
    irq_set_enabled(UART_IRQ, true);
    uart_set_irq_enables(UART_ID, true, false);

    sleep_ms(1000);

    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);

    glitch();

    uart_puts(UART_ID, "U-Boot 2020.04+fio+gcbb11e17ea (Aug 12 2021 - 23:27:31 +0000)");
    uart_puts(UART_ID, "\r\n");
    sleep_ms(200);
    uart_puts(UART_ID, "\r\n");
    sleep_ms(200);
    uart_puts(UART_ID, "[    0.000000] Booting Linux on physical CPU 0x0\r\n");
    uart_puts(UART_ID, "[    0.000000] Linux version 5.10.0-embedded\r\n");

    handle_spi_transaction();

    bootloader_countdown();
}
