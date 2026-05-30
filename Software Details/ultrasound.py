
# Ultrasonic Distance Measurement using HC-SR04 using time_pulse_us()
from machine import Pin, time_pulse_us
import time
# Define Trigger and Echo pins
trig = Pin(19, Pin.OUT)
echo = Pin(21, Pin.IN)
led = Pin(27, Pin.OUT)
distance1 = 0
while True:
    led.off()
    print("hello")
    # STEP 1: Send 10 µs Trigger Pulse
    trig.off()
    time.sleep_us(2)
    trig.on()
    time.sleep_us(10)
    trig.off()
    # STEP 2: Measure HIGH pulse duration on Echo pin
    # time_pulse_us(pin, pulse_level, timeout)
    # pin         → echo pin
    # pulse_level → 1 (measure HIGH pulse)
    # timeout     → maximum wait time in microseconds
    # Returns:
    #   Pulse duration in microseconds
    #   -1 if timeout waiting for pulse to start
    #   -2 if timeout waiting for pulse to end
    duration1 = time_pulse_us(echo, 1, 150000)
    start = time.ticks_ms()
    # 30 ms timeout
    # STEP 3: Check for Timeout Errors
    if duration1 < 0:
        print("no")
    else:
        print("og pos:")
        distance1 = duration1 / 58
        print(distance1)
    duration2 = time_pulse_us(echo, 1, 90000)
    end = time.ticks_ms()
    if duration2 < 0:
        print("no detection")
    else:
        # STEP 4: Convert Duration to Distance (cm)
        # distance(cm) = duration / 58
        # Derived from:
        # Distance = (Speed of Sound × Time) / 2
        distance2 = duration2 / 58
        print("distance2:")
        print(distance2)
        speed1 = distance1/start
        speed2 = distance2/end

        if speed1 - speed2  > 0:
            print("push detected")
        if speed1 - speed2 < 100:
            print("big push")
            hand = 0
            led.on()
        elif speed1 - speed2 < 200:
            print("med push")
            hand = 0
            led.on()
        elif speed1 - speed2 < 300:
            print("small push")
            hand = 0
            led.on()
    time.sleep(1)
