Waveshare LCD Display 24580

1.28" Round IPS LCD Touch Display - Waveshare 24580 (CircuitPython Guide)

First, the board has to be flashed with the current firmware of CircuitPython (It's right now: CircuitPython 9.0.5). You can find a detailed description of this here under the step 'Installing CircuitPython' at https://www.dgebhardt.de/pico-lcd-1.28-rund/download_pico_watch.html.

After that copy the required libraries into the 'lib' folder. These are at the moment:

cst816.py (touch sensor driver)

gc9a01.py (driver for the display)

adafruit_display_shapes (folder with drivers for graphical elements)
adafruit_display_text (folder with drivers for text labels)
adafruit_ticks.mpy (time measurement driver)

Adafruit's libraries can be found in the Adafruit-CircuitPython-bundle.

Try out the examples and also read the explanations on my website
https://www.dgebhardt.de/pico-lcd-1.28-rund/touch_display.html .

Example 1:

It is tested whether the connection to the CST816 touch sensor has been established. Then will
touch coordinates, gestures and press (True or False) retrieved. If that works, the touch sensor on the display
works perfectly.

Example 2:

The display is initialized and a rounded rectangle is shown in green color. If the rectangle
is touched, the color changes into blue. This allows testing the x- and y- coordinates on the display.

Example 3:

In this example, the gestures (up, down, left, right, long pressed) are shown on the display
