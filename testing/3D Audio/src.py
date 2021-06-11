from openal import *
import time
import random
import threading
import math
import sys

class thread_sound (threading.Thread):
    def __init__(self, x, y, z, tipo):
        threading.Thread.__init__(self)
        self.x = x
        self.y = y
        self.z = z
        self.tipo = tipo
    def run(self):
        play_sound(self.x,self.y,self.z,self.tipo)
        
def beep_beep(source):
    source.play()
    time.sleep(0.1)
    source.stop()
    time.sleep(0.05)
    source.play()
    time.sleep(0.1)
    source.stop()

def gradual_beep_beep(source):
    initial = source.gain
    gain = source.gain
    
    source.play()
    time.sleep(0.1)
    
    source.set_gain(0.0)
    time.sleep(0.1)
    source.stop()
    
    source.set_gain(initial)
    source.play()
    time.sleep(0.5)
    gain = source.gain
    while gain > 0.02:
        source.set_gain(gain)
        gain = gain - (gain/2)
        time.sleep(0.05)
    source.set_gain(0.0)
    time.sleep(0.2)
    source.stop()
    
def gradual_beep_long(source):
    source.play()
    gain = source.gain
    time.sleep(0.8)
    
    while gain > 0.02:
        source.set_gain(gain)
        gain = gain - (gain/2)
        time.sleep(0.1)
    
    source.set_gain(0.0)
    time.sleep(0.4)
    source.stop()

def gradual_beep_short(source):
    source.play()
    gain = source.gain
    
    while gain > 0.02:
        source.set_gain(gain)
        gain = gain - (gain/1.6)
        time.sleep(0.05)
    
    source.set_gain(0.0)
    time.sleep(0.7)
    source.stop()    
    
def sin_beep(source):
    source.play()
    x = 0.0
    original = source.gain
    print(original)
    while x < 1*(math.pi):
        source.set_gain(original*(math.sin(x)))
        x = x + 0.1
        time.sleep(0.05)
    
    source.set_gain(0.0)
    time.sleep(0.4)
    source.stop()
    
def play_sound(x,y,z,tipo):
    v = (0,0,0)
    listener = oalGetListener()
    listener.set_position(v)
    alDistanceModel(AL_EXPONENT_DISTANCE)
    
    waveFile = WaveFile("agudo5s.wav")
    buffer = Buffer(waveFile)

    source = Source(buffer)
    source.set_source_relative(True)
    v1 = (x,y,z)
    source.set_position(v1)
    source.set_reference_distance(0.5)
    source.set_rolloff_factor(0.5)
    
#     source.set_looping(True)
    pitch = random.random()/3 + 0.1
#     pitch = random.random()/5 + 0.1
#     pitch = 0.3
#     pitch = 0.2
    source.set_pitch(pitch)
  
    if tipo==1:
        beep_beep(source)
    if tipo==2:
        gradual_beep_short(source)
    if tipo==3:
        gradual_beep_long(source)
    if tipo==4:
        sin_beep(source)
    if tipo==5:
        gradual_beep_beep(source)
#    oalQuit()


# Create new threads
thread1 = thread_sound(-1, 1, 1, 2)

thread2 = thread_sound(0.5, 4, 1, 2)

# Start new Threads
thread1.start()
time.sleep(0.5)
thread2.start()

# playSound(2, 100, 2)
# playSound((random.random())*200 - 100,(random.random())*200 - 100,0)
# playSound((random.random())*200 - 100,(random.random())*200 - 100,0)