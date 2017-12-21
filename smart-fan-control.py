#!/usr/bin/env python

import subprocess


def get_hex_fan_speed(decimal_speed):
    return hex(decimal_speed << 2)[2:]


SMART_KEY = '194' # temperature celsius
SMART_COMMAND = [
   '/usr/local/bin/smartctl',
   '-A',
   '/dev/disk0'
]

SET_FAN_SPEED_COMMAND = [
    '/usr/local/sbin/smc',
    '-k', 'F1Mx',
    '-w', # needs hex speed as final arg
]

SPEEDS = {
    "31": 1100,
    "33": 1200,
    "35": 2000,
    "40": 2900,
    "44": 3800,
    "46": 4300,
    "48": 4700,
    "52": 5000,
}

HEXSPEEDS = {temp: get_hex_fan_speed(speed) for temp, speed in SPEEDS.iteritems()}


def print_speeds():
    print 'FAN SPEED SETTINGS:'
    for temp in sorted(SPEEDS.keys()):
        print "hdd temp: %s, speed: %s, speed hex: %s" % (temp, SPEEDS[temp], HEXSPEEDS[temp])


def get_temp():
    smart_output = subprocess.check_output(SMART_COMMAND).encode('utf8').split('\n')
    temp_line_array = filter(lambda line: SMART_KEY in line, smart_output)

    if not temp_line_array:
        raise Exception("Couldn't get temperature line from smartctl")

    temp_index = 9
    temp = temp_line_array[0].split()[temp_index].strip()
    return temp


def get_fan_speed(decimal_temp):
    sorted_speeds = [[temp, SPEEDS[temp]] for temp in sorted(SPEEDS.keys())]
    for temp, speed in sorted_speeds:
        if int(decimal_temp) <= int(temp):
            return speed
    else:
        # get the max speed from our array
        return sorted_speeds.pop()[1]


def set_fan_speed(hex_speed):
    subprocess.call(SET_FAN_SPEED_COMMAND + [hex_speed])


def main():
    print_speeds()

    try:
        temp = get_temp()
    except:
        temp = sorted(SPEEDS.keys()).pop()

    fan_speed = get_fan_speed(temp)
    hex_fan_speed = get_hex_fan_speed(fan_speed)
    print("Drive temperature is %s. Setting fan speed to %s (%s)" % (temp, fan_speed, hex_fan_speed))
    set_fan_speed(hex_fan_speed)


if __name__ == '__main__':
    main()
