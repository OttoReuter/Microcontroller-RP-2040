# SPDX-FileCopyrightText: 2023 Detlef Gebhardt, written for CircuitPython
# SPDX-FileCopyrightText: Copyright (c) 2023 Detlef Gebhardt
# SPDX-FileCopyrightText: based on a Waveshare template in Micropython
#
# SPDX-License-Identifier: GEBMEDIA
import board
import busio
import time

i2c_sda = board.GP6
i2c_sdl = board.GP7

class QMI8658:
    def __init__(self, address=0x6B):
        self._address = address
        self._bus = busio.I2C(scl=i2c_sdl, sda=i2c_sda, frequency=100_000)
        bRet = self.WhoAmI()
        if bRet:
            self.Read_Revision()
        else:
            return None
        self.Config_apply()

    def _read_byte(self, cmd):
        while not self._bus.try_lock():
            pass
        rec = bytearray(1)
        self._bus.readfrom_into(self._address, rec, start=cmd)
        return rec[0]

    def _read_block(self, reg, length=1):
        rec = bytearray(length)
        self._bus.writeto(0x6b, bytes([reg]))
        self._bus.readfrom_into(self._address, rec)
        return rec

    #def _read_u16(self, cmd):
    #    rec = bytearray(2)
    #    self._bus.readfrom_into(self._address, rec, start=cmd)
    #    return (rec[1] << 8) + rec[0]

    #def _write_byte(self, cmd, val):
    #    self._bus.writeto(self._address, bytes([cmd, val]))
    
    def WhoAmI(self):
        bRet = False
        while not self._bus.try_lock():
            pass
        self._bus.writeto(0x6b, bytes([0x05]))
        result = bytearray(2)
        self._bus.readfrom_into(0x6b, result)
        if result == bytearray(b'\x00\x00'):
            bRet = True
        return bRet

    def Read_Revision(self):
        self._bus.writeto(0x6b, bytes([0x01]))
        result = bytearray(2)
        self._bus.readfrom_into(0x6b, result)
        return result

    def Config_apply(self):
        # REG CTRL1
        self._bus.writeto(0x6b, bytes([0x02, 0x60]))
        result = bytearray(4)
        self._bus.readfrom_into(0x6b, result)
        # REG CTRL2 : QMI8658AccRange_8g  and QMI8658AccOdr_1000Hz
        self._bus.writeto(0x6b, bytes([0x03, 0x23]))
        result = bytearray(4)
        self._bus.readfrom_into(0x6b, result)
        # REG CTRL3 : QMI8658GyrRange_512dps and QMI8658GyrOdr_1000Hz
        self._bus.writeto(0x6b, bytes([0x04, 0x53]))
        result = bytearray(4)
        self._bus.readfrom_into(0x6b, result)
        # REG CTRL4 : No
        self._bus.writeto(0x6b, bytes([0x05, 0x00]))
        result = bytearray(4)
        self._bus.readfrom_into(0x6b, result)
        # REG CTRL5 : Enable Gyroscope And Accelerometer Low-Pass Filter
        self._bus.writeto(0x6b, bytes([0x06, 0x11]))
        result = bytearray(4)
        self._bus.readfrom_into(0x6b, result)
        # REG CTRL6 : Disables Motion on Demand.
        self._bus.writeto(0x6b, bytes([0x07, 0x00]))
        result = bytearray(4)
        self._bus.readfrom_into(0x6b, result)
        # REG CTRL7 : Enable Gyroscope And Accelerometer
        self._bus.writeto(0x6b, bytes([0x08, 0x03]))
        result = bytearray(4)
        self._bus.readfrom_into(0x6b, result)
    
    def Read_Raw_XYZ(self):
        xyz = [0, 0, 0, 0, 0, 0]
        raw_timestamp = self._read_block(0x30, 3)
        raw_acc_xyz = self._read_block(0x35, 12)
        raw_gyro_xyz = self._read_block(0x3b, 12)
        raw_xyz = self._read_block(0x35, 12)
        timestamp = (raw_timestamp[2] << 16) | (raw_timestamp[1] << 8) | (raw_timestamp[0])
        for i in range(6):
            # xyz[i]=(raw_acc_xyz[(i*2)+1]<<8)|(raw_acc_xyz[i*2])
            # xyz[i+3]=(raw_gyro_xyz[((i+3)*2)+1]<<8)|(raw_gyro_xyz[(i+3)*2])
            xyz[i] = (raw_xyz[(i * 2) + 1] << 8) | (raw_xyz[i * 2])
            if xyz[i] >= 32767:
                xyz[i] = xyz[i] - 65535
        return xyz

    def Read_XYZ(self):
        xyz = [0, 0, 0, 0, 0, 0]
        raw_xyz = self.Read_Raw_XYZ()
        # QMI8658AccRange_8g
        acc_lsb_div = 1 << 12
        # QMI8658GyrRange_512dps
        gyro_lsb_div = 64
        for i in range(3):
            xyz[i] = raw_xyz[i] / acc_lsb_div  # (acc_lsb_div/1000.0)
            xyz[i + 3] = raw_xyz[i + 3] * 1.0 / gyro_lsb_div
        return xyz

#if __name__=='__main__':
    # do nothing