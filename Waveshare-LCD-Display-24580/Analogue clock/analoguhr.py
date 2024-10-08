# SPDX-FileCopyrightText : 2024 Detlef Gebhardt, written for CircuitPython 8.2.4
# SPDX-FileCopyrightText : Copyright (c) 2024 Detlef Gebhardt
# SPDX-Filename          : Analoguhr mit Sekunde
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
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_ticks import ticks_ms
import gc9a01
import my_qmi8658
import my_cst816
import microcontroller

# Bitmap-Files
zifferblatt = "/images/zifferblatt.bmp"
second_zeiger = "/images/second.bmp"
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

# Clock face as background
bg_bitmap,bg_pal = adafruit_imageload.load(zifferblatt)
bg_tile_grid = displayio.TileGrid(bg_bitmap, pixel_shader=bg_pal)
main.append(bg_tile_grid)

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

#  pointer for seconds 30x140
bitmap_pointer_sec, palette_pointer = adafruit_imageload.load(second_zeiger, bitmap=displayio.Bitmap,palette=displayio.Palette)
palette_pointer.make_transparent(0)
# blank bitmap for the Second hand
bitmap_pointer_blank_sec = displayio.Bitmap(bitmap_pointer_sec.width, bitmap_pointer_sec.height, 1)

# Transparentes Overlay für 'rotozoom'
# pointer for rotation
bitmap_scribble_hour = displayio.Bitmap(display.width, display.height, len(palette_pointer))
tile_grid = displayio.TileGrid(bitmap_scribble_hour, pixel_shader=palette_pointer)
main.append(tile_grid)
bitmap_scribble_min = displayio.Bitmap(display.width, display.height, len(palette_pointer))
tile_grid = displayio.TileGrid(bitmap_scribble_min, pixel_shader=palette_pointer)
main.append(tile_grid)
bitmap_scribble_sec = displayio.Bitmap(display.width, display.height, len(palette_pointer))
tile_grid = displayio.TileGrid(bitmap_scribble_sec, pixel_shader=palette_pointer)
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

# show the function
roundrect_f= RoundRect(60,175,120,40,20,fill=0x009900, outline=0x00ff00)
timeset.append(roundrect_f)
#create the label function
updating_label_f = label.Label(font=terminalio.FONT, text="fertig", scale=2, color=0xffffff, line_spacing=1)
updating_label_f.anchor_point = (0, 0)
updating_label_f.anchored_position = (85, 180)
timeset.append(updating_label_f)

def uhr_stellen(h,m,month,day,weekday):
    # detect touchscreen
    point = touch.get_point()
    gesture = touch.get_gesture()
    press = touch.get_touch()
    gesture = 0
    # clock setting
    while True:
        gesture = touch.get_gesture()
        press = touch.get_touch()
        point = touch.get_point()
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
            if point.x_point < 30:
                r = rtc.RTC()
                r.datetime = time.struct_time((2024, month, day, h, m, 0, weekday, 1, -1))
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

if current_time.tm_year > 2020:
    with open("/time.txt", "w") as f:
        f.write(str(hour)+"\n")
        f.write(str(minute)+"\n")
    f.close()
    uhrstellen = False

if current_time.tm_year == 2020:
    with open("time.txt", "r") as f:
        hour = int(f.readline())
        minute = int(f.readline())
    f.close()
    rc = rtc.RTC()
    rc.datetime = time.struct_time((2024, month, day, hour, minute, 0, weekday, 1, -1)) 
    display.brightness = 1
    uhrstellen = True
    h=hour
    m=minute
    updating_label_instruction.text = "    set time\nhour:  up/down\nminute:right/left"
    updating_label2.text = "{:02}:{:02}".format(h,m)
    display.root_group = timeset
    # call the 'uhr_stellen' function
    uhr_stellen(h,m,month,day,weekday)
    uhrstellen = False

if hour > 12:
    hour = hour -12

display.root_group = main
display.refresh()
start = ticks_ms()
#ein = 0



while True:
    #read QMI8658
    xyz=sensor.Read_XYZ()
    wert_x = (10)*xyz[1]
    # detect touchscreen
    point = touch.get_point()
    gesture = touch.get_gesture()
    press = touch.get_touch()
    # display touched to reset
    if gesture == 12 and press == True:
        r3=(point.x_point - 120)*(point.x_point - 120) + (point.y_point - 120)*(point.y_point - 120)
        if r3 < 14400:
            microcontroller.reset()
    
    # time
    current_time = time.localtime()
    hour = current_time.tm_hour
    minute = current_time.tm_min
    second = current_time.tm_sec
    alpha_rad_sec = math.pi/30 * second
    bitmaptools.rotozoom( bitmap_scribble_sec, bitmap_pointer_sec, angle = alpha_rad_sec, px=15,py=107)
    alpha_rad_hour = math.pi/6 * hour + math.pi/180 * minute/2
    bitmaptools.rotozoom( bitmap_scribble_hour, bitmap_pointer_hour, angle = alpha_rad_hour, px=15,py=120)
    alpha_rad_min = math.pi/30 * minute
    bitmaptools.rotozoom( bitmap_scribble_min, bitmap_pointer_min, angle = alpha_rad_min, px=15,py=120)
    # einmal pro Minute speichern
    if second == 59:
        with open("/time.txt", "w") as f:
            f.write(str(hour)+"\n")
            f.write(str(minute+1)+"\n")
            f.write(str(day)+"\n")
        f.close()
    
    gc.collect()   
    #print(gc.mem_free())
