from machine import Pin, PWM
import time
m1 = Pin(13,Pin.OUT)
m2 =Pin(14,Pin.OUT)
m3 =Pin(15,Pin.OUT)
m4 =Pin(27,Pin.OUT)

m1.freq(50)
m2.freq(50)
m3.freq(50)
m4.freq(50)
hand = 1
def play():
    hand = 
    rise_thrust  = 80
    desc_thrust = 1023
    rt_pace = 10
    for i in range (200, 80, -(rt_pace)):# rise to the middle of the parabola, the starting point. # numbers refer to cms of height.
        m1.duty(rise_thrust+((i/100) * rise_thrust)) # 12 percent increases
        m2.duty(rise_thrust+((i/100) * rise_thrust))
        m3.duty(rise_thrust+((i/100) * rise_thrust))
        m4.duty(rise_thrust+((i/100) * rise_thrust))
    while True:
    for i in range (80, 200, (rt_pace)):# first descent
        m1.duty(rise_thrust-(((i/100) * rise_thrust)*2)) # targeted decrease thrust
        m2.duty(rise_thrust-(((i/100) * rise_thrust)*2))
        m3.duty(rise_thrust-((i/100) * rise_thrust)) #less thrust for directional change
        m4.duty(rise_thrust-((i/100) * rise_thrust)) #this needs to happen till detection is there?
        if hand == 0:
            break
        if (smallpush
        if medpush
        if big push
            
    ----
            if hand == 0:
            break