# Analogue clock

The round LCD display with motion and touch sensor is perfect for watch applications. Here I show you a variant as
a real analogue clock. CircuitPython newer than 9.0.5 uses too much memory for this application. That's why this application no longer runs. The watch has a second-, a minute- and a hour- hand. They stand out well against the dark Dial off.
If the clock is started on the PC, the time is synchronized to the second and over a long period of time
adhered to very precisely. After the battery has been completely discharged, this method should always be chosen
otherwise the date starts with January 1st, 2020 and the time is 00:00.
Now a saving process is provided so that the last time is always saved after 59 seconds. Because the time is stored
on the CIRCUITPY drive, the writing process must be enabled through the boot.py file. This is the case when the board
is restarted once. And the time.txt file must exist.

## The watch has the following functions:

- displays time with analogue hour-, minute- and second hands;
- control function using touch sensor after restart without PC. This can also be done during operation. It can be
  called up by pressing the center of the display.

## Setting up the clock:

Copy the following files to the 'CIRCUITPY' drive:

- into the /lib folder the current libraries adafruit_display_shapes, adafruit_display_text, adafruit_imageload and
  adafruit_ticks.mpy as well as the drivers gc9a01.py and my_qmi8658.py and my_cst816.py;
- the folder /images with the bitmap files of the hands for the seconds, minutes and hours;
- the file analoguhr.py , boot.py and time.txt.

## IMPORTANT NOTE:

The memory is almost completely occupied by the representation of the bitmap elements (dial and 3 pointers). Before
You use the program, flash the memory completely with the file 'flash_nuke.uf2' and then play the current firmware
from CircuiPython (currently CircuitPython 9.0.5) on the display. In my example the program shows every time the
loop is run 17,232 bytes as free. And this is only if you use 'gc.collect()' to free unneeded memory.

Another possibility is, for example, to transfer the firmware with the older version 8.2.4. and replace the Adafruit
libraries from the older bundle. In my tests it worked very well because the older firmware uses less memory.
