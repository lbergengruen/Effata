# import the necessary packages
import time
from openal import WaveFile, Buffer, Source
import math

# CONSTANTS
WAVE_FILE = WaveFile("../Sound/agudo5s.wav")


def play_sound(x, y, z):
    buffer = Buffer(WAVE_FILE)
    source = Source(buffer)

    source.set_source_relative(True)
    v1 = (x, y, z)
    source.set_position(v1)
    pitch = 0.12
    source.set_pitch(pitch)
    gradual_beep_long(source)


def play_pozo_sound(x, y, z):
    buffer = Buffer(WAVE_FILE)
    source = Source(buffer)

    source.set_source_relative(True)
    v1 = (x, y, z)
    source.set_position(v1)
    pitch = 0.2
    source.set_pitch(pitch)
    gradual_beep_long(source)

# def beep_beep(source):
#     source.play()
#     time.sleep(0.1)
#     source.stop()
#     time.sleep(0.05)
#     source.play()
#     time.sleep(0.1)
#     source.stop()
#
#
# def gradual_beep_short(source):
#     source.play()
#     gain = source.gain
#
#     while gain > 0.02:
#         source.set_gain(gain)
#         gain = gain - (gain / 1.6)
#         time.sleep(0.05)
#
#     source.set_gain(0.0)
#     time.sleep(0.7)
#     source.stop()


def gradual_beep_long(source):
    source.play()
    gain = source.gain
    time.sleep(0.8)

    while gain > 0.02:
        source.set_gain(gain)
        gain = gain - (gain / 2)
        time.sleep(0.1)

    source.set_gain(0.0)
    time.sleep(0.4)
    source.stop()


# def gradual_beep_beep(source):
#     initial = source.gain
#     gain = source.gain
#
#     source.play()
#     time.sleep(0.1)
#
#     source.set_gain(0.0)
#     time.sleep(0.1)
#     source.stop()
#
#     source.set_gain(initial)
#     source.play()
#     time.sleep(0.5)
#     gain = source.gain
#
#     while gain > 0.02:
#         source.set_gain(gain)
#         gain = gain - (gain / 2)
#         time.sleep(0.05)
#
#     source.set_gain(0.0)
#     time.sleep(0.2)
#     source.stop()
#
#
# def sin_beep(source):
#     source.play()
#     x = 0.0
#     original = source.gain
#     # print(original)
#
#     while x < 1 * math.pi:
#         source.set_gain(original * (math.sin(x)))
#         x = x + 0.1
#         time.sleep(0.05)
#
#     source.set_gain(0.0)
#     time.sleep(0.4)
#     source.stop()
