import time
from openal import *
import random
from random import randint

#CONSTANTES
WAVE_FILE = WaveFile("agudo5s.wav")


# class threadSound (threading.Thread):
#     def __init__(self, x, y, z):
#         threading.Thread.__init__(self)
#         self.x = x
#         self.y = y
#         self.z = z
#     def run(self):
#         playSound(self.x,self.y,self.z)
        
def beep_beep(source):
    source.play()
    time.sleep(0.1)
    source.stop()
    time.sleep(0.05)
    source.play()
    time.sleep(0.1)
    source.stop()
    
def gradual_beep(source):
    source.play()
    gain = 8.0
    
#     while gain > 0.02:
#         source.set_gain(gain)
#         gain = gain - (gain/1.6)
#         time.sleep(0.05)
    
#     source.set_gain(0.0)
    time.sleep(0.7)
    source.stop()

def play_sound(x,y,z):
    buffer = Buffer(WAVE_FILE)
    source = Source(buffer)
    
    source.set_source_relative(True)
    v1 = (x,y,z)
    source.set_position(v1)
    pitch = 0.5 + 0.3
    source.set_pitch(pitch)
    beep_beep(source)
#    gradual_beep(source)
#     oalQuit()