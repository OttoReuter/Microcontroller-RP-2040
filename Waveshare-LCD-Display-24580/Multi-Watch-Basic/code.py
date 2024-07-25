# SPDX-FileCopyrightText : 2024 Detlef Gebhardt, written for CircuitPython 9.0.5
# SPDX-FileCopyrightText : Copyright (c) 2024 Detlef Gebhardt
# SPDX-Filename          : smartwatch for Waveshare round 1.28 touch LCD
# SPDX-License-Identifier: https://dgebhardt.de
import time
import gc
import board
import busio
import rtc
import displayio
import terminalio
import gc9a01
import my_cst816
import my_qmi8658
import analogio
from adafruit_display_text import label
from adafruit_ticks import ticks_ms
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.line import Line
import adafruit_imageload
import bitmaptools

weg = "/images/symbol3.bmp"
wdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Release any resources currently in use for the displays
displayio.release_displays()
# Make the displayio SPI bus and the GC9A01 display
spi = busio.SPI(clock=board.GP10, MOSI=board.GP11)
display_bus = displayio.FourWire(spi, command=board.GP8, chip_select=board.GP9, reset=board.GP13)
display = gc9a01.GC9A01(display_bus, width=240, height=240, backlight_pin=board.GP25)
display.rotation = 90
display.brightness = 1

# Initialize den I2C-Bus
i2c_sda = board.GP6
i2c_scl = board.GP7
i2c = busio.I2C(scl=i2c_scl, sda=i2c_sda)

# Initialize the Sensors
touch = my_cst816.CST816(i2c)
#touch.set_mode(3)
sensor = my_qmi8658.QMI8658(i2c)

# Make the display context
main_screen = displayio.Group()
group1_screen = displayio.Group()
splash = displayio.Group()

# make analogio for voltage
adc = analogio.AnalogIn(board.GP27)
spannung = (adc.value * adc.reference_voltage) / 65535 * 6

######
# beginning of main_screen
######
# make bitmap for the display background
background = displayio.Bitmap(240, 240, 1)
mypal = displayio.Palette(3)
mypal[0] = 0x800000
background.fill(0)
# Background oben
main_screen.append(displayio.TileGrid(background, pixel_shader=mypal))
# Background unten
background2 = Rect(0, 140, 240, 100, fill=0xc0c0c0)
main_screen.append(background2)
line = Line(120,170,120,220,color=0x000000)
main_screen.append(line)

# show the batterysymbol
roundrect1= RoundRect(90,15,30,8,3,fill=None, outline=0xffffff)
main_screen.append(roundrect1)
roundrect2= RoundRect(91,16,20,6,1,fill=0x00cc00, outline=None)
main_screen.append(roundrect2)
#create the label for volt
updating_label_volt = label.Label(font=terminalio.FONT, text="3,7 V", scale=1, color=0xffffff, line_spacing=1)
updating_label_volt.anchor_point = (0, 0)
updating_label_volt.anchored_position = (130, 15)
main_screen.append(updating_label_volt)

# show the roundrect for the steps
roundrect_f= RoundRect(40,120,160,40,20,fill=0x009900, outline=0x00ff00)
main_screen.append(roundrect_f)
#create the label for the steps
updating_label_f = label.Label(font=terminalio.FONT, text="", scale=2, color=0xffffff, line_spacing=1)
updating_label_f.anchor_point = (0, 0)
updating_label_f.anchored_position = (65, 125)
main_screen.append(updating_label_f)

# create the label for the time - hour and minute
updating_label_time = label.Label(font=terminalio.FONT, text="", scale=3, color=0xffffcc, line_spacing=1)
updating_label_time.anchor_point = (0, 0)
updating_label_time.anchored_position = (70, 40)
main_screen.append(updating_label_time)
# create the label for the time-second
updating_label_sec = label.Label(font=terminalio.FONT, text="", scale=2, color=0xffffcc, line_spacing=1)
updating_label_sec.anchor_point = (0, 0)
updating_label_sec.anchored_position = (165, 50)
main_screen.append(updating_label_sec)
# create the label for the day
updating_label_day = label.Label(font=terminalio.FONT, text="", scale=2, color=0xffffcc)
updating_label_day.anchor_point = (0, 0)
updating_label_day.anchored_position = (40, 85)
main_screen.append(updating_label_day)

# pictogramm stopwatch/breakfast egg
bitmap_weg, palette_weg = adafruit_imageload.load(weg, bitmap=displayio.Bitmap,palette=displayio.Palette)
palette_weg.make_transparent(0)
bitmap_weg_blank = displayio.Bitmap(bitmap_weg.width, bitmap_weg.height, 1)
# transparent overlay for 'rotozoom'
bitmap_scribble = displayio.Bitmap(display.width, display.height, len(palette_weg))
tile_grid = displayio.TileGrid(bitmap_scribble, pixel_shader=palette_weg)
main_screen.append(tile_grid)
#bitmaptools.rotozoom( bitmap_scribble, bitmap_weg, angle = 0, px=45,py=-80)
bitmaptools.rotozoom( bitmap_scribble, bitmap_weg, angle = 0, px=40,py=-60)

#######
# End of main_screen
#######
#######
# Beginning of group1_screen
#######

# display background
background_func = displayio.Bitmap(240, 240, 1)
pal_color = displayio.Palette(3)
pal_color[0] = 0x800000
pal_color[1] = 0x008000
pal_color[2] = 0x008080
#background_func.fill(0)
group1_screen.append(displayio.TileGrid(background_func, pixel_shader=pal_color))
# Background unten
background2 = Rect(0, 110, 240, 240, fill=0xc0c0c0)
group1_screen.append(background2)

# create the label for instruction
updating_label_instruction = label.Label(font=terminalio.FONT, text="", scale=2, color=0xffffcc, line_spacing=1)
updating_label_instruction.anchor_point = (0, 0)
updating_label_instruction.anchored_position = (30, 20)
group1_screen.append(updating_label_instruction)

# create a label (Uhr stellen)
updating_label2 = label.Label(font=terminalio.FONT, text="", scale=5, color=0x000000,line_spacing=1)
updating_label2.anchor_point = (0, 0)
updating_label2.anchored_position = (50, 120)
group1_screen.append(updating_label2)

# create a label (Stopuhr)
updating_label3 = label.Label(font=terminalio.FONT, text="", scale=5, color=0x000000,line_spacing=1)
updating_label3.anchor_point = (0, 0)
updating_label3.anchored_position = (50, 120)
group1_screen.append(updating_label3)

#######
# End of group1_screen
#######
#######
# Beginning of screen splash
#######

# Make the background bitmap
color_bitmap = displayio.Bitmap(240, 240, 3)
color_palette = displayio.Palette(3)
color_palette[0] = 0x03C2FC
color_palette[1] = 0xFFFFFF  # White
color_palette[2] = 0xFF0000  # red
bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

def alarm():
    display.root_group = splash
    i = 0
    for i in range(10):
        color_bitmap.fill(0)
        time.sleep(0.1)
        color_bitmap.fill(1)
        time.sleep(0.1)
        color_bitmap.fill(2)
        time.sleep(0.1)
#######
# End of screen splash
#######
      
def uhr_stellen(h,m,uhr,month,day,weekday):
    # clock setting
    while True:
        gesture = touch.get_gesture()
        press = touch.get_touch()
        if gesture == 2 and press == True: # up (minute)
            m += 1
            if m > 59:
                m = 0
            updating_label2.text = "{:02}:{:02}".format(h,m)
            time.sleep(0.5)
        if gesture == 1 and press == True: # down (minute)
            m -= 1
            if m < 0:
                m = 59
            updating_label2.text = "{:02}:{:02}".format(h,m)
            time.sleep(0.5)
        if gesture == 4 and press == True: # right (hour)
            h += 1
            if h > 23:
                h = 0
            updating_label2.text = "{:02}:{:02}".format(h,m)
            time.sleep(0.5)
        if gesture == 3 and press == True: # left (hour)
            h -= 1
            if h < 1:
                h = 23
            updating_label2.text = "{:02}:{:02}".format(h,m)
            time.sleep(0.5)
        # clock set leave
        if gesture == 12 and press == True:
            r = rtc.RTC()
            r.datetime = time.struct_time((2024, month, day, h, m, 0, weekday, 1, -1))
            display.root_group = main_screen
            display.refresh()
            time.sleep(0.5)
            break

def stop_uhr(timing):
    stopzeit = ticks_ms()
    uhr = 0
    time.sleep(0.5)
    # start stopwatch
    while True:
        gesture = touch.get_gesture()
        press = touch.get_touch()
        if uhr == 2:
            timing= int((ticks_ms() - stopzeit)/100)/10
            haltzeit = timing
            if timing < 60:
                updating_label3.text = str(timing) + " s"
            else:
                updating_label3.text = "{:02}:{:02}".format(int(timing//60),int(timing%60))
        # start
        if gesture == 0 and press == True and timing == 0:
            uhr = 2
            stopzeit = ticks_ms()
            time.sleep(0.5)
        # stop
        if gesture == 0 and press == True and timing > 0:
            uhr = 0
            if haltzeit < 60:
                updating_label3.text = str(haltzeit) + " s"
            else:
                updating_label3.text = "{:02}:{:02}".format(int(haltzeit//60),int(haltzeit%60))
            time.sleep(0.5)
        # repetition
        if gesture == 0 and press == True:
            timing = 0
            stopzeit = ticks_ms()
        # stopwatch leave
        if gesture == 12 and press == True:
            updating_label3.text = ""
            display.root_group = main_screen
            display.refresh()
            time.sleep(0.5)
            break

def uhr_timer():
    m = 0
    h = 0
    uhr = 0
    now = 0
    dest = 0
    difference = 0
    updating_label3.text = "{:02}:00".format(m)
    # start timer
    while True:
        gesture = touch.get_gesture()
        press = touch.get_touch()
        current_time = time.localtime()
        hour = current_time.tm_hour
        minute = current_time.tm_min
        second = current_time.tm_sec
        if gesture == 4 and press == True: # right (minute)
            m += 1
            if m > 59:
                m = 0
            updating_label3.text = "{:02}:00".format(m)
            time.sleep(0.5)
            uhr = 3
            
        if gesture == 3 and press == True: # left (minute)
            m -= 1
            if m < 0:
                m = 59
            updating_label3.text = "{:02}:00".format(m)
            time.sleep(0.5)
            uhr = 3
           
        # show remaining time
        if uhr == 2:
            now = hour*3600 + minute*60 + second
            difference = dest - now
            haltzeit = difference
            updating_label3.text = "{:02}:{:02}".format(int(difference//60),int(difference%60))
        # start
        if gesture == 12 and press == True and uhr == 3:
            uhr = 2
            dest = (hour + h)*3600 + (minute+m)*60 + second
            time.sleep(0.5)
        # stop
        if gesture == 0 and press == True and difference > 0:
            uhr = 0
            if haltzeit < 60:
                updating_label3.text = str(haltzeit) + " s"
            else:
                updating_label3.text = "{:02}:{:02}".format(int(haltzeit//60),int(haltzeit%60))
            time.sleep(0.5)
        # alarm when destination reached
        if difference < 0 and uhr == 2:
            updating_label3.text = "00:00"
            alarm()
            uhr = 0
            updating_label3.text = ""
            display.root_group = main_screen
            break   
        #
        # timer leave
        if gesture == 12 and press == True and uhr == 0:
            updating_label3.text = ""
            display.root_group = main_screen
            display.refresh()
            time.sleep(0.5)
            break
            
# Variable
start = ticks_ms()
disp_hell = ticks_ms()
display.root_group = main_screen
long = 10
uhr = 0
uhrstellen = False
stopuhr = False
timer = False
step = 175
stepstop = 0

while True:
    current_time = time.localtime()
    hour = current_time.tm_hour
    minute = current_time.tm_min
    second = current_time.tm_sec
    month = current_time.tm_mon
    day = current_time.tm_mday
    weekday = current_time.tm_wday
    #
    # prepare time string for display
    # 
    if uhr == 0:
        zeit = "{:02}:{:02}".format(hour,minute)
        updating_label_time.text = zeit 
        updating_label_sec.text = ":{:02}".format(second)
        updating_label_day.text = "{:02}.{:02}. ".format(day,month) + wdays[weekday]
    #
    # read ACC sensor
    #
    reading = sensor.Read_XYZ()
    wert_y = (10)*reading[0]
    wert_x = (10)*reading[1]
    wert_z = (10)*reading[2]
    #
    # detect touchscreen
    #
    point = touch.get_point()
    gesture = touch.get_gesture()
    press = touch.get_touch()
    distance = touch.get_distance()
    #
    # display brightness
    #
    if (ticks_ms() - disp_hell)/1000 > long:
        display.brightness = 0.01
    # Brightness responds to short movements on the left arm
    if wert_x < -4:
        display.brightness = 1
        disp_hell = ticks_ms()
    #
    # count steps
    #
    # Move your arm up to count
    if (abs(wert_x) > 6 and abs(wert_z) > 4 and stepstop ==0):
        start = ticks_ms()
        step += 1
        stepstop = 1            
     # Move your arm back down
    if (abs(wert_x) < 5 and abs(wert_z) < 3 and stepstop == 1):
         if (ticks_ms() - start)> 1000:
            stepstop = 0
    # show steps
    updating_label_f.text = str(step) + "/6000"
    
    #
    # select clock setting
    #
    r2=(point.x_point - 180)*(point.x_point - 180) + (point.y_point - 120)*(point.y_point - 120)
    if r2 < 2500 and press == True and stopuhr == False and timer == False:
        display.brightness = 1
        uhrstellen = True
        h=hour
        m=minute
        uhr = 1
        updating_label_instruction.text = "   set time\nmin.: left/right\nhour: up/down"
        updating_label2.text = "{:02}:{:02}".format(h,m)
        display.root_group = group1_screen
        background_func.fill(0)
        # call the 'uhr_stellen' function
        uhr_stellen(h,m,uhr,month,day,weekday)
        uhrstellen = False
        disp_hell = ticks_ms()
        uhr = 0
    #
    # select stopwatch 
    #
    r3=(point.x_point - 45)*(point.x_point - 45) + (point.y_point - 75)*(point.y_point - 75)
    if r3 < 900 and press == True and uhrstellen == False and timer == False:
        display.brightness = 1
        stopuhr = True
        m = 0
        s = 0
        timing = 0
        updating_label_instruction.text = "    Stopuhr\n     click\n   start/stop"
        updating_label2.text = ""
        updating_label3.text = "0.0 s"
        display.root_group = group1_screen
        background_func.fill(1)
        # call the 'stop_uhr' function
        stop_uhr(timing)
        stopuhr = False
        disp_hell = ticks_ms()
        uhr = 0
    #
    # select timer
    #
    r4=(point.x_point - 45)*(point.x_point - 45) + (point.y_point - 165)*(point.y_point - 165)
    if r4 < 900 and press == True and uhrstellen == False and stopuhr == False:
        display.brightness = 1
        timer = True
        updating_label_instruction.text = "     timer\n     click\n   start/stop"
        updating_label2.text = ""
        updating_label3.text = "00:00"
        display.root_group = group1_screen
        background_func.fill(1)
        # call the 'timer' function
        uhr_timer()
        timer = False
        disp_hell = ticks_ms()
        uhr = 0
    #
    # update voltage once per minute
    #
    if second == 59:
        # Spannung anzeigen
        spannung = (adc.value * adc.reference_voltage) / 65535 * 6
        updating_label_volt.text = str(int(spannung*10)/10) + " V"

    gc.collect()
    #print(gc.mem_free())