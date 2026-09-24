#include "pico/stdlib.h"
#include "hardware/spi.h"

// Hardware-Pins für das Display (SPI0)
#define DISPLAY_SPI_PORT   spi0
#define PIN_DISPLAY_SCLK   18
#define PIN_DISPLAY_MOSI   19
#define PIN_DISPLAY_DC     17
#define PIN_DISPLAY_RST    20
#define PIN_DISPLAY_CS     21

void lcd_write_cmd(uint8_t cmd) {
    gpio_put(PIN_DISPLAY_DC, 0); // DC auf Low für Befehle
    gpio_put(PIN_DISPLAY_CS, 0);
    spi_write_blocking(DISPLAY_SPI_PORT, &cmd, 1);
    gpio_put(PIN_DISPLAY_CS, 1);
}

void lcd_write_data(uint8_t data) {
    gpio_put(PIN_DISPLAY_DC, 1); // DC auf High für Daten
    gpio_put(PIN_DISPLAY_CS, 0);
    spi_write_blocking(DISPLAY_SPI_PORT, &data, 1);
    gpio_put(PIN_DISPLAY_CS, 1);
}

void lcd_init() {
    // SPI0-Schnittstelle mit 31.25 MHz initialisieren
    spi_init(DISPLAY_SPI_PORT, 31250 * 1000);
    gpio_set_function(PIN_DISPLAY_SCLK, GPIO_FUNC_SPI);
    gpio_set_function(PIN_DISPLAY_MOSI, GPIO_FUNC_SPI);

    // Steuerleitungen als normale GPIO-Ausgänge konfigurieren
    gpio_init(PIN_DISPLAY_DC);
    gpio_set_dir(PIN_DISPLAY_DC, GPIO_OUT);
    gpio_init(PIN_DISPLAY_RST);
    gpio_set_dir(PIN_DISPLAY_RST, GPIO_OUT);
    gpio_init(PIN_DISPLAY_CS);
    gpio_set_dir(PIN_DISPLAY_CS, GPIO_OUT);

    // Hardware-Reset des Displays durchführen
    gpio_put(PIN_DISPLAY_RST, 0);
    sleep_ms(50);
    gpio_put(PIN_DISPLAY_RST, 1);
    sleep_ms(50);

    // ST7789 Startsequenz für 240x320 im Landscape-Modus
    lcd_write_cmd(0x01); // Software Reset
    sleep_ms(150);

    lcd_write_cmd(0x11); // Sleep Out
    sleep_ms(255);

    lcd_write_cmd(0x3A); // Interface Pixel Format
    lcd_write_data(0x05); // 16-Bit Farbmodus (RGB565)

    lcd_write_cmd(0x36); // Memory Data Access Control
    lcd_write_data(0x70); // Rotation auf Querformat (MX, MV gesetzt)

    lcd_write_cmd(0x29); // Display On
    sleep_ms(20);
}
