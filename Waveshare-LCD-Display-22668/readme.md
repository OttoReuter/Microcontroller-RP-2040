# Waveshare LCD Display 22668
## 1.28" Round IPS LCD Display - Waveshare 22668 
## with 6 axis ACC/Gyroscope sensor (CircuitPython Guide)

The round LCD display with motion sensor is perfect for watch applications. At first I show you one variant with a
digital time display. Instead of analog clock-hands, a second dot (white), a minute dot (green) and a hour dot
(red) moves on the outer circle of the display.

First, the board has to be flashed with the current firmware of CircuitPython (It's right now: CircuitPython 9.0.5).
You can find a detailed description of this here under the step 'Installing CircuitPython' at
https://www.dgebhardt.de/pico-lcd-1.28-rund/download_pico_watch.html.

After that copy the required libraries into the 'lib' folder. These are:

my_qmi8658.py (driver for the acc sensor)
gc9a01.py (driver for the display)

adafruit_display_shapes (folder with drivers for graphical elements), adafruit_display_text (folder with drivers for
text labels) and adafruit_ticks.mpy (time measurement driver). Adafruit's libraries can be found in the
Adafruit-CircuitPython-bundle.
