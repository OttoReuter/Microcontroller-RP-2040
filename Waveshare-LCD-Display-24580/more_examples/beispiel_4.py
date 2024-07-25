import time
import gc
import board
import busio
import displayio
import terminalio
import gc9a01
import my_cst816
import my_qmi8658
from adafruit_display_text import label
from adafruit_ticks import ticks_ms
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.line import Line

# Release any resources currently in use for the displays
displayio.release_displays()
# Make the displayio SPI bus and the GC9A01 display
spi = busio.SPI(clock=board.GP10, MOSI=board.GP11)
display_bus = displayio.FourWire(spi, command=board.GP8, chip_select=board.GP9, reset=board.GP13)
display = gc9a01.GC9A01(display_bus, width=240, height=240, backlight_pin=board.GP25)
display.rotation = 90
display.brightness = 1

# Initialisiere den I2C-Bus
i2c_sda = board.GP6
i2c_scl = board.GP7
i2c = busio.I2C(scl=i2c_scl, sda=i2c_sda)

# Initialisiere beide Sensoren
touch = my_cst816.CST816(i2c)
#touch.set_mode(1)
accsensor = my_qmi8658.QMI8658(i2c)

# Make the display context
main_screen = displayio.Group()
display.root_group = main_screen

# make bitmap for the display background
background = displayio.Bitmap(240, 240, 1)
mypal = displayio.Palette(3)
mypal[0] = 0x800000
background.fill(0)
# Background oben
main_screen.append(displayio.TileGrid(background, pixel_shader=mypal))
# Background unten
background2 = Rect(0, 120, 240, 120, fill=0xc0c0c0)
main_screen.append(background2)

# create the label for acc
updating_label = label.Label(font=terminalio.FONT, text="", scale=2, color=0xffffcc, line_spacing=1)
updating_label.anchor_point = (0, 0)
updating_label.anchored_position = (50, 40)
main_screen.append(updating_label)

# create the label for touch-point
updating_label2 = label.Label(font=terminalio.FONT, text="", scale=2, color=0x0000cc, line_spacing=1)
updating_label2.anchor_point = (0, 0)
updating_label2.anchored_position = (40, 135)
main_screen.append(updating_label2)

aus = True

while True:
    point = touch.get_point()
    #print(touch.x_point, touch.y_point)
    gesture = touch.get_gesture()
    press = touch.get_touch()
    reading = accsensor.Read_XYZ()
    acc_x = int((100) * reading[0]) / 10
    acc_y = int((100) * reading[1]) / 10
    acc_z = int((100) * reading[2]) / 10
    updating_label.text = "acc_x= " + str(acc_x) + "\nacc_y= " + str(acc_y) + "\nacc_z= " + str(acc_z)
    updating_label2.text = "touch.x_point,\ntouch.y_point\n   " + str(touch.x_point) + ", " + str(touch.y_point)
    #
    # Displayhelligkeit
    #
    if touch.x_point > 120 and touch.x_point < 240 and press == True and aus == True:
        display.brightness = 0.01
        aus = False
    if touch.x_point > 0 and touch.x_point < 120 and press == True and aus == False:
        display.brightness = 1
        aus = True
    time.sleep(0.5)
