# SPDX-FileCopyrightText : 2024 Detlef Gebhardt, written for CircuitPython 8.2.4
# SPDX-FileCopyrightText : Copyright (c) 2024 Detlef Gebhardt
# SPDX-Filename          : pico-watch
# SPDX-License-Identifier: https://dgebhardt.de
import time
import gc
import rtc
import board
import busio
import displayio
import digitalio
import terminalio
import bitmaptools
import math
import adafruit_imageload
from adafruit_display_text import label
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.line import Line
from adafruit_ticks import ticks_ms
import gc9a01
import my_qmi8658
import my_cst816
import microcontroller

# Variable definieren
wdays = ["Mon", "Tue", "Wed", "Thur", "Fri", "Sat", "Sun"]

# Bitmap-Files
raspberry = "/images/raspberry.bmp"
minute_zeiger = "/images/min_zeiger.bmp"
hour_zeiger = "/images/hour_zeiger.bmp"

# Initialize the I2C-Bus
i2c_sda = board.GP6
i2c_scl = board.GP7
i2c = busio.I2C(scl=i2c_scl, sda=i2c_sda)

# Initialize the Sensors
touch = my_cst816.CST816(i2c)
sensor = my_qmi8658.QMI8658(i2c)

# Release any resources currently in use for the displays
displayio.release_displays()

# Make the displayio SPI bus and the GC9A01 display
spi = busio.SPI(clock=board.GP10, MOSI=board.GP11)
display_bus = displayio.FourWire(spi, command=board.GP8, chip_select=board.GP9, reset=board.GP13)
display = gc9a01.GC9A01(display_bus, width=240, height=240, backlight_pin=board.GP25)
display.rotation = 90
display.brightness = 1

main = displayio.Group()
timeset = displayio.Group()

# Text
text_area = label.Label(terminalio.FONT, text="", line_spacing=0.9, color=0xffffff, anchor_point=(0.5,0.5), anchored_position=(0,0))
text_group = displayio.Group(scale=1, x=120, y=80)
text_group.append(text_area)
main.append(text_group)
## create the label for time
updating_label1 = label.Label(font=terminalio.FONT, text="", scale=2, color=0xffffff, line_spacing=1)
# set label position on the display and add label
updating_label1.anchor_point = (0, 0)
updating_label1.anchored_position = (75, 90)
main.append(updating_label1)

# Pictogramm raspberry
bitmap_berry, palette_berry = adafruit_imageload.load(raspberry, bitmap=displayio.Bitmap,palette=displayio.Palette)
palette_berry.make_transparent(0)
bitmap_berry_blank = displayio.Bitmap(bitmap_berry.width, bitmap_berry.height, 1)
# transparent overlay for 'rotozoom'
bitmap_scribble = displayio.Bitmap(display.width, display.height, len(palette_berry))
tile_grid = displayio.TileGrid(bitmap_scribble, pixel_shader=palette_berry)
main.append(tile_grid)
bitmaptools.rotozoom( bitmap_scribble, bitmap_berry, angle = 0, px=15,py=-30)

radius = 120
xpos = 120
ypos = 120
# short lines per second
for i in range(60):
    line = Line(xpos+int(115*math.cos(i*math.pi/30)),ypos-int(115*math.sin(i*math.pi/30)),
                xpos+int(radius*math.cos(i*math.pi/30)), ypos-int(radius*math.sin(i*math.pi/30)),0xaaaaaa)
    main.append(line)
# longer lines per minute
for i in range(12):
    line = Line(xpos+int(110*math.cos(i*math.pi/6)),ypos-int(110*math.sin(i*math.pi/6)),
                xpos+int(120*math.cos(i*math.pi/6)), ypos-int(120*math.sin(i*math.pi/6)),0xffff00)
    main.append(line)
# ring with the numbers
for i in range(1,13,1):
    updating_label = label.Label(
        font=terminalio.FONT, text=str(i), scale=2, color=0xffffff,
        line_spacing=1)
    #set label position on the display and add label
    updating_label.anchor_point = (0, 0)
    updating_label.anchored_position = (xpos-5+int(95*math.cos(-1*i*math.pi/6+ math.pi/2)),
                                        ypos-10-int(95*math.sin(-1*i*math.pi/6+ math.pi/2)))
    main.append(updating_label)
# secondpoint
circle_sec = Circle(xpos, ypos, 5, fill=0xff0000, outline=0x000000 )
main.append(circle_sec)

# pointer for the hour 30x140
bitmap_pointer_hour, palette_pointer = adafruit_imageload.load(hour_zeiger, bitmap=displayio.Bitmap,palette=displayio.Palette)
palette_pointer.make_transparent(0)
# blank bitmap for the hour pointer
bitmap_pointer_blank_hour = displayio.Bitmap(bitmap_pointer_hour.width, bitmap_pointer_hour.height, 1)

# pointer for minutes 30x140
bitmap_pointer_min, palette_pointer = adafruit_imageload.load(minute_zeiger, bitmap=displayio.Bitmap,palette=displayio.Palette)
palette_pointer.make_transparent(0)
# blank bitmap for the minute hand
bitmap_pointer_blank_min = displayio.Bitmap(bitmap_pointer_min.width, bitmap_pointer_min.height, 1)

# Transparentes Overlay für 'rotozoom'
# pointer for rotation
bitmap_scribble_hour = displayio.Bitmap(display.width, display.height, len(palette_pointer))
tile_grid = displayio.TileGrid(bitmap_scribble_hour, pixel_shader=palette_pointer)
main.append(tile_grid)
bitmap_scribble_min = displayio.Bitmap(display.width, display.height, len(palette_pointer))
tile_grid = displayio.TileGrid(bitmap_scribble_min, pixel_shader=palette_pointer)
main.append(tile_grid)
circle1 = Circle(120, 120, 10, fill=0xff0000, outline=None)
main.append(circle1)
circle2 = Circle(120, 120, 5, fill=0x000000, outline=0x0)
main.append(circle2)

# create the label for instruction
updating_label_instruction = label.Label(font=terminalio.FONT, text="", scale=2, color=0xffffcc, line_spacing=1)
updating_label_instruction.anchor_point = (0, 0)
updating_label_instruction.anchored_position = (30, 20)
timeset.append(updating_label_instruction)
# create a label (time set)
updating_label2 = label.Label(font=terminalio.FONT, text="", scale=5, color=0xffffff,line_spacing=1)
updating_label2.anchor_point = (0, 0)
updating_label2.anchored_position = (50, 100)
timeset.append(updating_label2)

def uhr_stellen(h,m):
    # detect touchscreen
    point = touch.get_point()
    gesture = touch.get_gesture()
    press = touch.get_touch()
    gesture = 0
    # clock setting
    while True:
        gesture = touch.get_gesture()
        press = touch.get_touch()
        if gesture == 2 and press == True: # up (minute)
            m += 1
            if m > 59:
                m = 0
            updating_label2.text = "{:02}:{:02}".format(h,m)
            gesture = 0
            time.sleep(0.5)
        if gesture == 1 and press == True: # down (minute)
            m -= 1
            if m < 0:
                m = 59
            updating_label2.text = "{:02}:{:02}".format(h,m)
            gesture = 0
            time.sleep(0.5)
        if gesture == 4 and press == True: # right (hour)
            h += 1
            if h > 23:
                h = 0
            updating_label2.text = "{:02}:{:02}".format(h,m)
            gesture = 0
            time.sleep(0.5)
        if gesture == 3 and press == True: # left (hour)
            h -= 1
            if h < 0:
                h = 23
            updating_label2.text = "{:02}:{:02}".format(h,m)
            gesture = 0
            time.sleep(0.5)
        # clock set leave
        if gesture == 12 and press == True:
            r = rtc.RTC()
            r.datetime = time.struct_time((2024, 1, 1, h, m, 0, 0, 1, -1))
            display.root_group = main
            display.refresh()
            gesture = 0
            time.sleep(1)
            break

display.refresh()
current_time = time.localtime()
hour = current_time.tm_hour
minute = current_time.tm_min
second = current_time.tm_sec
month = current_time.tm_mon
day = current_time.tm_mday
weekday = current_time.tm_wday

if current_time.tm_year == 2020:
    text_area.text = "pico-watch"
    display.brightness = 1
    uhrstellen = True
    h=hour
    m=minute
    updating_label_instruction.text = "    set time\nhour:  up/down\nminute:right/left"
    updating_label2.text = "{:02}:{:02}".format(h,m)
    display.root_group = timeset
    # call the 'uhr_stellen' function
    uhr_stellen(h,m)
    uhrstellen = False
else:
    text_area.text = wdays[weekday] + "  {:02}.{:02}.".format(day,month)

if hour > 12:
    hour = hour -12

display.root_group = main
display.refresh()
start = ticks_ms()
ein = 0


while True:
    #read QMI8658
    xyz=sensor.Read_XYZ()
    wert_x = (10)*xyz[1]
    # detect touchscreen
    point = touch.get_point()
    #gesture = touch.get_gesture()
    press = touch.get_touch()
    # Brightness responds to short movements on the left arm
    if wert_x < -4:
        display.brightness = 1
        start = ticks_ms()
        ein = 1
    # display brightness
    if (ticks_ms() - start)/1000 > 15:
        display.brightness = 0.01
        ein = 0
    # display touched to reset
    r3=(point.x_point - 120)*(point.x_point - 120) + (point.y_point - 120)*(point.y_point - 120)
    if r3 < 900 and press == True and ein == 1:
        microcontroller.reset()
    if r3 < 900 and press == True and ein == 0:
        display.brightness = 1
        time.sleep(1)
        start = ticks_ms()
        ein = 1
    # time
    current_time = time.localtime()
    hour = current_time.tm_hour
    minute = current_time.tm_min
    second = current_time.tm_sec
    alpha_rad_hour = math.pi/6 * hour + math.pi/180 * minute/2
    bitmaptools.rotozoom( bitmap_scribble_hour, bitmap_pointer_hour, angle = alpha_rad_hour, px=15,py=120)
    alpha_rad_min = math.pi/30 * minute
    bitmaptools.rotozoom( bitmap_scribble_min, bitmap_pointer_min, angle = alpha_rad_min, px=15,py=120)
    #
    # set the second point
    #
    xpos_neu = int(120 + 115*math.cos((second -15)*math.pi/30))
    delta_sec_x = xpos_neu - xpos
    xpos = xpos_neu
    ypos_neu = int(120 + 115*math.sin((second -15)*math.pi/30))
    delta_sec_y = ypos_neu - ypos
    ypos = ypos_neu
    circle_sec.x = circle_sec.x + delta_sec_x
    circle_sec.y = circle_sec.y + delta_sec_y 
    gc.collect()   
    #print(gc.mem_free())