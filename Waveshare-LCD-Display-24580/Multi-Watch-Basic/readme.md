# Multi-Watch Basic

The clock displays the current time, date and day of the week. In a separate field they are the steps from
this day displayed. They are registered by the motion sensor when worn on the arm. When the display is
powered by a 3.7 volt lipo-battery, the existing voltage can be read in the upper area. To save power, the
display brightness is reduced. With an arm movement towards the viewer switches the display to 'bright'. If
the clock is started on the PC, the time is synchronized to the nearest second and adhered to very precisely
over a long time. After the battery was completely discharged this method should be always used, otherwise
the date starts at January 1st, 2020 and the time is 00:00. A saving process is not provided for the Basic variant.

## The watch has the following functions:
- A touch on the time switches to a screen where the time can be set;
- Touching the stopwatch-bitmap switches to a screen with a stopwatch function;
- Touching the breakfast-egg- bitmap switches to a screen with a timer function;
- To save power, the display goes dark after 10 seconds (not in the function screens)
  and switches back to bright when the arm is moved.
- Steps are counted when arm movements (up and down, like when walking or running). The startpoint and
  setpoint value is specified as a variable in the program and can be adjusted as desired.

## Setting up the clock:

Copy the following files into the 'CIRCUITPY' drive:
- /images folder with the file symbol3.bmp;
- in the /lib folder the libraries adafruit_display_shapes, adafruit_display_text, adafruit_imageload
  and adafruit_ticks.mpy as well as the drivers my_cst816.py and my_qmi8658.py;
- the file code.py

## Note on the battery and housing:

In one of my other projects, I gave important information on the polarity of the Lipo-battery and also
presented a housing on my website. To see this, go to https://www.dgebhardt.de/komplett_aw/pico-watch-magix.html.

