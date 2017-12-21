#!/usr/bin/env python

import sys
import subprocess


class GetTemperatureException(Exception):
    pass


class GetFanSpeedException(Exception):
    pass


class InvalidFanSpeedException(Exception):
    pass


class FanControl:
    SMART_COMMAND = ['/usr/local/bin/smartctl', '-A', '/dev/disk0']
    # NOTE: check your SMART command output and set this variable appropriately
    # this is the lookup key for the hard drive temperature in celsius.
    # it could be `190`, `194`, or something else depending on your hard drive.
    # - Key 190: Airflow_Temperature_Cel
    SMART_TEMPERATURE_KEY = '194'
    # the column holding the temperature in the SMART command output
    SMART_TEMPERATURE_COLUMN_INDEX = 9

    # Sets the *maximum* fan speed. This brings the speed down from an
    # artifically high level due to the lack of HDD sensor data after
    # replacing the stock iMac hard drive. Otherwise the HDD fan would
    # run at max speed (6000+) all the time.
    SET_FAN_SPEED_COMMAND = [
        '/usr/local/sbin/smc',
        '-k', 'F1Mx',
        '-w',  # needs hex speed as final arg
    ]

    MAX_SPEED = 6200
    # maps temperature to fan speed
    SPEEDS = {
        '31': 1100,
        '33': 1200,
        '35': 1500,
        '38': 2300,
        '41': 2900,
        '44': 3800,
        '46': 4300,
        '48': 4700,
        '52': 5000,
    }

    def __init__(self):
        self.sorted_speeds = [[temperature, self.SPEEDS[temperature]]
                              for temperature in sorted(self.SPEEDS.keys())]

    def get_hex_fan_speed(self, decimal_speed):
        return hex(decimal_speed << 2)[2:]

    def print_speeds(self):
        print('FAN SPEED SETTINGS:')
        template = 'hdd temp: %s, speed: %s, hex speed: %s'
        for temperature, speed in self.sorted_speeds:
            hex_speed = self.get_hex_fan_speed(speed)
            print(template % (temperature, speed, hex_speed))

    def get_temp(self):
        try:
            smart_output = subprocess.check_output(self.SMART_COMMAND).encode('utf8').split('\n')
            smart_line = filter(lambda line: self.SMART_TEMPERATURE_KEY in line, smart_output)[0]
            temperature = smart_line.split()[self.SMART_TEMPERATURE_COLUMN_INDEX].strip()
            return temperature
        except:
            raise GetTemperatureException('Couldn\'t get temperature line from smartctl')

    def get_fan_speed(self, decimal_temperature):
        for temperature, speed in self.sorted_speeds:
            if int(decimal_temperature) <= int(temperature):
                return speed
        else:
            raise GetFanSpeedException('Couldn\'t get fan speed for temperature')

    def validate_decimal_speed(self, decimal_speed):
        min_speed = self.sorted_speeds[0][1]
        max_speed = self.MAX_SPEED
        if min_speed <= decimal_speed <= max_speed:
            return True
        else:
            raise InvalidFanSpeedException('Fan speed was out of the allowed range')

    def validate_hex_speed(self, hex_speed):
        decimal_speed = int(hex_speed, base=16) >> 2
        return self.validate_decimal_speed(decimal_speed)

    def set_fan_speed_to_decimal(self, decimal_speed):
        self.validate_decimal_speed(decimal_speed)
        hex_speed = self.get_hex_fan_speed(decimal_speed)
        subprocess.call(self.SET_FAN_SPEED_COMMAND + [hex_speed])

    def set_fan_speed_to_hex(self, hex_speed):
        self.validate_hex_speed(hex_speed)
        subprocess.call(self.SET_FAN_SPEED_COMMAND + [hex_speed])

    def auto_set_fan_speed(self):
        try:
            temperature = self.get_temp()
            fan_speed = self.get_fan_speed(temperature)
        except:
            temperature = 'TEMP_NOT_FOUND'
            fan_speed = self.MAX_SPEED

        hex_fan_speed = self.get_hex_fan_speed(fan_speed)
        print('Drive temperature is %s. Setting fan speed to %s (%s).' % (temperature, fan_speed, hex_fan_speed))
        self.set_fan_speed_to_hex(hex_fan_speed)


def main():
    arg_len = len(sys.argv)
    command = sys.argv[1] if arg_len > 1 else None

    fan_control = FanControl()

    if arg_len < 2:
        fan_control.auto_set_fan_speed()
    elif command == 'print':
        fan_control.print_speeds()
    elif command == 'set':
        decimal_speed = int(sys.argv[2])
        fan_control.set_fan_speed_to_decimal(decimal_speed)
    else:
        print('The command you entered is not supported.')


if __name__ == '__main__':
    main()
