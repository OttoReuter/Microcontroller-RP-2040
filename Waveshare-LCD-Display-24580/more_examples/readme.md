# description

So far I have only used the CST816 driver for the touch sensor. The display also has a 6-axis
ACC and Gyroskop sensor. It is a QMI8658 sensor that is connected via i2c like the CST816. Both on our display
via i2c_scl = board.GP7 and i2c_sda = board.GP6. However, the cst816.py in examples 1 to 3 was from the author(s):
NeoStormer integrated with i2c_device. But it can only control one i2c device. That's why I have the cst816.py driver
changed to my_cst816.py, just like the driver my_qmi8658.py, which didn't exist for CircuitPython either.

Replace both drivers with my_cst816.py and my_qmi8658.py to use both sensors at the same time from now.

This is exactly what example 4 does. It shows acc_1 to acc_3 in the upper display area and the x and y coordinate
of touch.x_point and touch.y_point in the lower area. If you tap on the display, it's not just that coordinates
changes. You turn the brightness off in the upper area and turn it back on at the bottom (display.brightness). Note,
that the coordinates appear to be swapped because the display is rotated 90 degrees. That's how I use it in my
Clock applications.
