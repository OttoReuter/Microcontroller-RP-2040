#include <stdio.h>
#include "pico/stdlib.h"
#include "pico/bootrom.h"
#include "hardware/spi.h"
#include "hardware/gpio.h"
#include "hardware/watchdog.h"

// Externe Display-Initialisierung einbinden
extern void lcd_init(void);

// Hardware-Pins für die SD-Karte (SPI1)
#define SD_SPI_PORT        spi1
#define PIN_SD_SCK         10
#define PIN_SD_MOSI        11
#define PIN_SD_MISO        12
#define PIN_SD_CS          13

// Hardware-Pins für das Gaming-Board (Tastenmatrix)
#define PIN_KEY_UP         4
#define PIN_KEY_DOWN       5
#define PIN_KEY_LEFT       3
#define PIN_KEY_RIGHT      2
#define PIN_KEY_A          7  // Bestätigen / Flashen
#define PIN_KEY_B          6  // Zurück
#define PIN_KEY_C          9  // Zusatzfunktion / Direktstart
#define PIN_KEY_D          8  // System-Reboot

// Flash-Adressen für das verschobene Spieleprofil
#define FLASH_TARGET_OFFSET (512 * 1024)          // 512 KB Offset im Flash
#define XIP_BASE            0x10000000
#define FLASH_BASE_ADDRESS  (XIP_BASE + FLASH_TARGET_OFFSET) // 0x10080000
#define VECTOR_TABLE_ADDR   (FLASH_BASE_ADDRESS + 256)        // Vektortabelle (Boot2 übersprungen)

// Tasten initialisieren (Input mit Pull-Up, da Schaltung gegen GND)
void init_keys() {
    uint8_t key_pins[] = {PIN_KEY_UP, PIN_KEY_DOWN, PIN_KEY_LEFT, PIN_KEY_RIGHT, PIN_KEY_A, PIN_KEY_B, PIN_KEY_C, PIN_KEY_D};
    for (int i = 0; i < 8; i++) {
        gpio_init(key_pins[i]);
        gpio_set_dir(key_pins[i], GPIO_IN);
        gpio_pull_up(key_pins[i]);
    }
}

// Die Kern-Funktion: Springt via Hardware-Watchdog gezielt in das verschobene Spiel
void launch_game() {
    // Cache löschen, um stabil die echten Flash-Inhalte zu lesen
    flash_flush_cache();
    sleep_ms(20);

    // Vektortabelle des Spiels bei 0x10080100 auslesen
    uint32_t* vector_table = (uint32_t*)VECTOR_TABLE_ADDR;
    uint32_t game_stack_pointer = vector_table[0];
    uint32_t game_reset_handler = vector_table[1];

    // Sicherheits-Prüfung: Liegt dort überhaupt ein gültiger Programmcode?
    if (game_reset_handler == 0xFFFFFFFF || game_reset_handler == 0) {
        // Fehlerfall: Kein gültiges Spiel im Flash vorhanden!
        return;
    }

    // Gezielter Hardware-Reboot: Setzt Register zurück und bootet nach 10ms direkt in das Spiel
    watchdog_reboot(game_reset_handler, game_stack_pointer, 10);

    while (1) {
        tight_loop_contents();
    }
}

int main() {
    // Standard-Peripherie (wie USB-Serial) initialisieren
    stdio_init_all();

    // Dein ST7789 Display über SPI0 aufwecken
    lcd_init();

    // Deine Tastenmatrix mit Pull-Ups vorbereiten
    init_keys();

    // Native SPI1-Schnittstelle für die SD-Karte konfigurieren
    spi_init(SD_SPI_PORT, 12000 * 1000); // 12 MHz für stabile SD-Übertragung
    gpio_set_function(PIN_SD_SCK, GPIO_FUNC_SPI);
    gpio_set_function(PIN_SD_MOSI, GPIO_FUNC_SPI);
    gpio_set_function(PIN_SD_MISO, GPIO_FUNC_SPI);
    
    gpio_init(PIN_SD_CS);
    gpio_set_dir(PIN_SD_CS, GPIO_OUT);
    gpio_put(PIN_SD_CS, 1);

    // Hauptschleife des Loaders
    while (1) {
        // Beispiel-Abfrage: Wenn Taste C (GPIO 9) gedrückt wird, direkt das Spiel im Flash starten
        if (gpio_get(PIN_KEY_C) == 0) {
            launch_game();
        }

        // Wenn Taste D (GPIO 8) gedrückt wird, einen sauberen System-Kaltstart durchführen
        if (gpio_get(PIN_KEY_D) == 0) {
            watchdog_reboot(0, 0, 0);
        }

        sleep_ms(50); // Entprell-Verzögerung und CPU-Schonung
    }

    return 0;
}
