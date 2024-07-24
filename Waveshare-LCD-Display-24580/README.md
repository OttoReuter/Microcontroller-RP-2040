Waveshare LCD Display 24580

1.28" Round IPS LCD Touch Display - Waveshare 24580 (CircuitPython Guide)

First, the board has to be flashed with the current firmware of CircuitPython (It's right now: CircuitPython 9.0.5). You can find a detailed description of this here under the step 'Installing CircuitPython' at https://www.dgebhardt.de/pico-lcd-1.28-rund/download_pico_watch.html.

After that copy the required libraries into the 'lib' folder. These are at the moment:

cst816.py (touch sensor driver)
gc9a01.py (driver for the display)
adafruit_display_shapes (folder with drivers for graphical elements)
adafruit_display_text (folder with drivers for text labels)
adafruit_ticks.mpy (time measurement driver)

Try out the examples and also read the explanations on my website
https://www.dgebhardt.de/pico-lcd-1.28-rund/touch_display.html .

