
import time
import board
import busio
import displayio
import terminalio
import gc9a01
import cst816
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
display = gc9a01.GC9A01(display_bus, width=240, height=240, backlight_pin=board.GP25, brightness = 1)
display.rotation = 0

##Touch Pins
# I2C_SDA = 6
# I2C_SDL = 7
# I2C_INT = 17
# I2C_RST = 16
# Initialize I2C
i2c = busio.I2C(scl=board.GP7, sda=board.GP6)
touch = cst816.CST816(i2c)
touch.set_mode(3)

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

#create the label
updating_label = label.Label(font=terminalio.FONT, text="direction", scale=2, color=0xffffff, line_spacing=1)
updating_label.anchor_point = (0, 0)
updating_label.anchored_position = (75, 110)
main_screen.append(updating_label)

while True:
    point = touch.get_point()
    gesture = touch.get_gesture()
    press = touch.get_touch()
    if display.rotation == 0:
        if gesture == 1 and press == True: # up
            updating_label.text = "Hoch"
            time.sleep(0.5)
        if gesture == 2 and press == True: # down
            updating_label.text = "Runter"
            time.sleep(0.5)
        if gesture == 3 and press == True: # left
            updating_label.text = "Links"
            time.sleep(0.5)
        if gesture == 4 and press == True: # right
            updating_label.text = "rechts"
            time.sleep(0.5)
        if gesture == 5 and press == True: # double click
            updating_label.text = "Doubleclick"
            time.sleep(1)
        if gesture == 12 and press == True: # long
            updating_label.text = "long pressed"
            time.sleep(1)
        print(gesture)
    gesture = 0
  
