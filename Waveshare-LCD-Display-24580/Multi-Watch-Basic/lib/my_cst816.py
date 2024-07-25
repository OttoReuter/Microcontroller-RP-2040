# SPDX-FileCopyrightText: 2024 Detlef Gebhardt, written for CircuitPython
# SPDX-FileCopyrightText: Copyright (c) 2024 Detlef Gebhardt
# SPDX-FileCopyrightText: based on a Waveshare template in Micropython
#
# SPDX-License-Identifier: dgebhardt.de
import busio
import time

_CST816_IrqCtl = const(0xFA)
_CST816_MotionMask = const(0xAA)
_CST816_Point_Mode = const(1)
_CST816_Gesture_Mode = const(2)
_CST816_ALL_Mode = const(3)


class CST816:
    """Driver for the CST816 Touchscreen connected over I2C."""
    def __init__(self, i2c, address=0x15):
        self._bus = i2c
        self._address = address
        self.prev_x = 0
        self.prev_y = 0
        self.prev_touch = False
        self.x_point = 0
        self.y_point = 0
        self.x_dist = 0
        self.y_dist = 0
        self.mode = 0

    def _i2c_write(self, reg, value):
        """Write to I2C"""
        while not self._bus.try_lock():
            pass
        self._bus.writeto(0x15, bytes([reg]))
        value = bytearray(2)
        self._bus.readfrom_into(0x15, value)
        return value
        self._bus.unlock()

    def _i2c_read(self, reg):
        """Read from I2C"""
        #while not self._bus.try_lock():
        #    pass
        self._bus.writeto(0x15, bytes([reg]))
        data = bytearray(1)          
        self._bus.readfrom_into(0x15, data)
        return data[0]
        #self._bus.unlock()

    def who_am_i(self):
        """Check the Chip ID"""
        return bool(self._i2c_read(0xA7) == 0xB5)

    def reset(self):
        """Make the Chip Reset"""
        self._i2c_write(0xFE, 0x00)
        time.sleep(0.1)
        self._i2c_write(0xFE, 0x01)
        time.sleep(0.1)

    def read_revision(self):
        """Read Firmware Version"""
        return self._i2c_read(0xA9)

    def wake_up(self):
        """Make the Chip Wake Up"""
        self._i2c_write(0xFE, 0x00)
        time.sleep(0.01)
        self._i2c_write(0xFE, 0x01)
        time.sleep(0.05)
        self._i2c_write(0xFE, 0x01)

    def stop_sleep(self):
        """Make the Chip Stop Sleeping"""
        self._i2c_write(0xFE, 0x01)

    def set_mode(self, mode):
        """Set the Behaviour Mode"""
        if mode == 1:
            self._i2c_write(0xFA, 0x41)
        elif mode == 2:
            self._i2c_write(0xFA, 0x11)
            self._i2c_write(0xAA, 0x01)
        else:
            self._i2c_write(0xFA, 0x71)
        self.mode = mode

    def get_point(self):
        """Get the Pointer Position"""
        x_point_h = self._i2c_read(0x03)
        x_point_l = self._i2c_read(0x04)
        y_point_h = self._i2c_read(0x05)
        y_point_l = self._i2c_read(0x06)
        self.x_point = ((x_point_h & 0x0F) << 8) + x_point_l
        self.y_point = ((y_point_h & 0x0F) << 8) + y_point_l
        return self

    def get_gesture(self):
        """Get the Gesture made by the User"""
        gesture = self._i2c_read(0x01)
        return gesture

    def get_touch(self):
        """Detect User Presence, are they touching the screen?"""
        finger_num = self._i2c_read(0x02)
        return finger_num > 0

    def get_distance(self):
        """Get the Distance made Between Readings, only while touched"""
        touch_data = self.get_point()
        x = touch_data.x_point
        y = touch_data.y_point
        if self.prev_touch is False and self.get_touch() is True:
            self.x_dist = 0
            self.y_dist = 0
        else:
            self.x_dist = x - self.prev_x
            self.y_dist = y - self.prev_y
        self.prev_touch = self.get_touch()
        self.prev_x = x
        self.prev_y = y
        return self

#if __name__=='__main__':
    # do nothing