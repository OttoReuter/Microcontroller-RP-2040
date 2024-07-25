# SPDX-FileCopyrightText : 2024 Detlef Gebhardt, written for CircuitPython 9.0.5
# SPDX-FileCopyrightText : Copyright (c) 2024 Detlef Gebhardt
# SPDX-Filename          : pico-watch-magix
# SPDX-License-Identifier: https://dgebhardt.de
import time
import gc
import board
import rtc
import busio
from busio import I2C
import displayio
import terminalio
import gc9a01
import my_qmi8658
from adafruit_display_text import label
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_ticks import ticks_ms
import random
import math

# Release any resources currently in use for the displays
displayio.release_displays()

# Waveshare 22668 Display
# 
lcd_rst = board.GP12
# Waveshare 24580 touch Display
#
#lcd_rst = board.GP13

# Make the displayio SPI bus and the GC9A01 display
spi = busio.SPI(clock=board.GP10, MOSI=board.GP11)
display_bus = displayio.FourWire(spi, command=board.GP8, chip_select=board.GP9, reset=lcd_rst)
display = gc9a01.GC9A01(display_bus, width=240, height=240, rotation=90, backlight_pin=board.GP25)

# Make the display context
group1 = displayio.Group()
display.root_group = group1

i2c_sda = board.GP6
i2c_sdl = board.GP7
i2c = busio.I2C(scl=i2c_sdl, sda=i2c_sda, frequency=100_000)

# acc sensor initialize
sensor=my_qmi8658.QMI8658(i2c)

width = 240
height = 240
xpos = 120
ypos = 120
radius = 120
i = 0

# Make some circles and lines:
circle = Circle(xpos, ypos, 120, fill=0xae2323, outline=0x000000)
group1.append(circle)
circle = Circle(xpos, ypos, 115, fill=0x000000, outline=0x000000)
group1.append(circle)
# lines for seconds
for i in range(60):
    line = Line(xpos+int(105*math.cos(i*math.pi/30)),ypos-int(105*math.sin(i*math.pi/30)),
                xpos+int(110*math.cos(i*math.pi/30)), ypos-int(110*math.sin(i*math.pi/30)),0xffffff)
    group1.append(line)
    display.root_group = group1
circle = Circle(xpos, ypos, 100, fill=0x726b6b, outline=0x726b6b)
group1.append(circle)
circle = Circle(xpos, ypos, 95, fill=0x282323, outline=0x000000)
group1.append(circle)
# lines for hours
for i in range(12):
    line = Line(xpos+int(95*math.cos(i*math.pi/6)),ypos-int(95*math.sin(i*math.pi/6)),
                xpos+int(90*math.cos(i*math.pi/6)), ypos-int(90*math.sin(i*math.pi/6)),0xffffff)
    group1.append(line)
    display.root_group = group1
circle = Circle(xpos, ypos, 80, fill=0x726b6b, outline=0x726b6b)
group1.append(circle)
circle = Circle(xpos, ypos, 75, fill=0x282323, outline=0x000000)
group1.append(circle)

circle_sec = Circle(xpos, ypos, 4, fill=0x726b6b, outline=0xffffaa)
group1.append(circle_sec)

xpos_min = 120
ypos_min = 33
xpos_hour = 120
ypos_hour = 52

# green point for minute
circle_min = Circle(xpos_min,ypos_min, 5, fill=0x726b6b, outline=0x00cc00)
group1.append(circle_min)
# red point for hour
#circle_hour = Circle(xpos_hour, ypos_hour, 5, fill=0xff0000, outline=0xff0000)
circle_hour = Circle(xpos_hour, ypos_hour, 5, fill=0x726b6b, outline=0xff3333)
group1.append(circle_hour)

# roundrect
roundrect1 = RoundRect(60, 100, 120, 45, 10, fill=0x282323, outline=0xae2323, stroke=3)
group1.append(roundrect1)

## create the time-label
updating_label1 = label.Label(font=terminalio.FONT, text="", scale=2, color=0xffffaa,line_spacing=1)
# set label position on the display and add label
updating_label1.anchor_point = (0, 0)
updating_label1.anchored_position = (65, 110)
group1.append(updating_label1)
display.root_group = group1

## create the label for the title
label1 = label.Label(font=terminalio.FONT, text="  magic\n\n\npico-time", scale=2, color=0x282323,line_spacing=1)
# set label position on the display and add label
label1.anchor_point = (0, 0)
label1.anchored_position = (68, 65)
group1.append(label1)
display.root_group = group1

current_time = time.localtime()
hour = current_time.tm_hour
minute = current_time.tm_min
second = current_time.tm_sec

start = ticks_ms()
ein = 0
a = 0

while True:
    # read QMI8658
    xyz=sensor.Read_XYZ()
    if 5*xyz[1] < -1 and ein == 0:
        start = ticks_ms()
        ein = 1
        roundrect1.outline = 0xae2323
        updating_label1.color =  0xffffaa
        label1.color = 0x282323
        circle_min.fill = 0x726b6b
        circle_hour.fill = 0x726b6b
    if (ticks_ms() - start)/ 1000 > 3:
        if 5*xyz[1] >= -1:
            roundrect1.outline = 0x282323
            updating_label1.color =  0x282323
            label1.color = 0xffffaa
            circle_min.fill = 0xffffff
            circle_hour.fill = 0xffffff
            circle_sec.fill = 0xffffff
            ein = 0
    # display time
    current_time = time.localtime()
    hour = current_time[3]
    minute = current_time[4]
    second = current_time[5]
    zeit = "{:02}:{:02} Uhr".format(hour,minute)
    updating_label1.text = zeit 
    if ein == 0:
        minute = random.randint(0,59)
        # roll dots until the display moves
        for i in range(minute):
            xyz=sensor.Read_XYZ()
            if 5*xyz[1] < -1:
                ein = 0
                break
            xpos_min_neu = int(width/2 + 88*math.cos((i-minute-45)*math.pi/30))
            delta_min_x = xpos_min_neu - xpos_min
            xpos_min = xpos_min_neu
            ypos_min_neu = int(height/2 + 88*math.sin((i-minute-45)*math.pi/30))
            delta_min_y = ypos_min_neu - ypos_min
            ypos_min = ypos_min_neu
            circle_min.x = circle_min.x + delta_min_x
            circle_min.y = circle_min.y + delta_min_y
            xpos_hour_neu = int(width/2 + 68*math.cos((minute-i-45)*math.pi/30))
            delta_hour_x = xpos_hour_neu - xpos_hour
            xpos_hour = xpos_hour_neu
            ypos_hour_neu = int(height/2 + 68*math.sin((minute-i-45)*math.pi/30))
            delta_hour_y = ypos_hour_neu - ypos_hour
            ypos_hour = ypos_hour_neu
            circle_hour.x = circle_hour.x + delta_hour_x
            circle_hour.y = circle_hour.y + delta_hour_y
            time.sleep(0.05)
        # backward
        for i in range(minute,0,-1):
            xyz=sensor.Read_XYZ()
            if 5*xyz[1] < -1:
                ein = 0
                break
            xpos_min_neu = int(width/2 + 88*math.cos((i-minute-45)*math.pi/30))
            delta_min_x = xpos_min_neu - xpos_min
            xpos_min = xpos_min_neu
            ypos_min_neu = int(height/2 + 88*math.sin((i-minute-45)*math.pi/30))
            delta_min_y = ypos_min_neu - ypos_min
            ypos_min = ypos_min_neu
            circle_min.x = circle_min.x + delta_min_x
            circle_min.y = circle_min.y + delta_min_y
            xpos_hour_neu = int(width/2 + 68*math.cos((minute-i-45)*math.pi/30))
            delta_hour_x = xpos_hour_neu - xpos_hour
            xpos_hour = xpos_hour_neu
            ypos_hour_neu = int(height/2 + 68*math.sin((minute-i-45)*math.pi/30))
            delta_hour_y = ypos_hour_neu - ypos_hour
            ypos_hour = ypos_hour_neu
            circle_hour.x = circle_hour.x + delta_hour_x
            circle_hour.y = circle_hour.y + delta_hour_y
            time.sleep(0.05)
        circle_min.outline = 0x282323
        circle_hour.outline = 0x282323
        circle_min.fill = 0x282323
        circle_hour.fill = 0x282323
    circle_min.outline = 0x00cc00
    circle_hour.outline = 0xff3333
    circle_min.fill = 0x726b6b
    circle_hour.fill = 0x726b6b
    # minute set on display
    xpos_min_neu = int(width/2 + 88*math.cos((minute-15)*math.pi/30))
    delta_min_x = xpos_min_neu - xpos_min
    xpos_min = xpos_min_neu
    ypos_min_neu = int(height/2 + 88*math.sin((minute-15)*math.pi/30))
    delta_min_y = ypos_min_neu - ypos_min
    ypos_min = ypos_min_neu
    circle_min.x = circle_min.x + delta_min_x
    circle_min.y = circle_min.y + delta_min_y
    gc.collect()
    # hour set on display
    xpos_hour_neu = int(width/2 + int(68*math.cos((hour)*math.pi/6 + minute/2*math.pi/180 - math.pi/2)))
    delta_hour_x = xpos_hour_neu - xpos_hour
    xpos_hour = xpos_hour_neu
    ypos_hour_neu = int(height/2 + int(68*math.sin((hour)*math.pi/6 + minute/2*math.pi/180 - math.pi/2)))
    delta_hour_y = ypos_hour_neu - ypos_hour
    ypos_hour = ypos_hour_neu
    circle_hour.x = circle_hour.x + delta_hour_x
    circle_hour.y = circle_hour.y + delta_hour_y
    # second set on display
    xpos_neu = int(width/2 + 108*math.cos((second -15)*math.pi/30))
    delta_x = xpos_neu - xpos
    xpos = xpos_neu
    ypos_neu = int(height/2 + 108*math.sin((second -15)*math.pi/30))
    delta_y = ypos_neu - ypos
    ypos = ypos_neu
    circle_sec.x = circle_sec.x + delta_x
    circle_sec.y = circle_sec.y + delta_y
    gc.collect()
    #print(gc.mem_free())
