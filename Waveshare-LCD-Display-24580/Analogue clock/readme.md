# Analogue clock

The round LCD display with motion and touch sensor is perfect for watch applications. I show you here a variant as
a real analogue clock. It has a second-, a minute- and a hour- hand. They stand out well against the dark Dial off.
The day of the week and the date are displayed on the dial.
If the clock is started on the PC, the time is synchronized to the second and over a long period of time
adhered to very precisely. After the battery has been completely discharged, this method should always be chosen
otherwise the date starts with January 1st, 2020 and the time is 00:00.
A saving process is not provided for in this variant.

## The watch has the following functions:

- displays time with analogue hour-, minute- and second hands;
- displays date and day of the week;
- control function using touch sensor after restart without PC. This can also be done during operation. It can be
  called up by pressing the center of the display.
- to save power, the display brightness is reduced every 10 seconds and by means of
  motion sensor set back to 'bright';

## Setting up the clock:

Copy the following files to the 'CIRCUITPY' drive:

- in the /lib folder the current libraries adafruit_display_shapes, adafruit_display_text, adafruit_imageload and
  adafruit_ticks.mpy as well as the drivers gc9a01.py and my_qmi8658.py and my_cst816.py
- the file analoguhr.py or analoguhr_min.py as code.py

## IMPORTANT NOTE:

The memory is almost completely occupied by the representation of the bitmap elements (dial and 3 pointers). Before
You use the program, flash the memory completely with the file 'flash_nuke.uf2' and then play the current firmware
from CircuiPython (currently CircuitPython 9.1.1) on the display. In my example the program shows every time the
loop is run 17,232 bytes as free. And this is only if you use 'gc.collect()' to free unneeded memory. If you still
get a MemoryError, you can delete all program lines for the the second hand. Replace the second hand with a second
dot to save memory. The bitmap for the dial should also be replaced. To do this, use the file 'analoguhr_min.py'.
