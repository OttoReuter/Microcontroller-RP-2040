![pico-watch-magic](https://github.com/user-attachments/assets/5e46a02e-8b9a-4579-9f99-d6bd2a332be7)
# Pico Watch Magic

Here I show you one variant with a digital time display. Instead of analog clock-hands, a second dot (white),
a minute dot (green) and a hour dot (red) moves on the outer circle of the display. If the watch is not
moved, the digital display disappears and the minute- and hour points rotate seemingly uncoordinated. This
attracts the attention of observers and makes the watch particularly interesting. As soon as the clock is moved,
the digital display appears again with the current time.

If the clock is started on the PC, the time is synchronized to the second and over a long period of time
adhered to very precisely. After the battery has been completely discharged, this method should always be chosen
otherwise the date starts with January 1st, 2020 and the time is 00:00. A saving process is not provided for in
this variant.

## The watch has the following functions:

- displays the time digital and analog;
- to save power, the display brightness is reduced every 10 seconds and the
  minute-point and hour-points rotate visibly; 

## Setting up the clock:

Copy the following files to the 'CIRCUITPY' drive:

- in the /lib folder the libraries adafruit_display_shapes, adafruit_display_text and adafruit_ticks.mpy
  as well as the drivers gc9a01.py and my_qmi8658.py
- the file code.py

## notice:

You can also use the program with the Waveshare LCD display 24580. But then it must be noted that
'lcd_rst = board.GP13' is changed.
