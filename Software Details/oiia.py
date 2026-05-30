#oiaaaaaaaa
import time
from machine import Pin, PWM
import asyncio
import _thread
import random
user_switch = Pin(25, Pin.IN, Pin.PULL_UP)
strobe = PWM(Pin(26, Pin.OUT))
strobe.freq(1000)
og_oiia = [1.455, 1.77, 1.433, 1.465, 1.5, 1.5, 0.771, 0.7, 0.7, 0.6, 1.7, 1, 1.4, 1.3, 1.5, 1.3, 1.5, 1.4, 1.3, 1.5, 1.2, 1.4, 1.3, 1.4, 1.1, 1.6, 1.2, 1.5] #oiia og moving list
user_oiia = []
count_intensity = 0
correct_responses = 0
error_cushion = 0.003
humanerror_count = 0

def strobe_task(): # CLAUDE SOLN 1
    for i in range (10000000, 1): # strobe light on pwm with original oiia movements.
        strobe.duty((random.randint(20,1020)))
        time.sleep(0.2)
        
#async def strobe_task(): claude soln 2
#    for val in og_oiia:
#        strobe.duty(val * 600)
#        await asyncio.sleep(0.2)

_thread.start_new_thread(strobe_task, ()) #needed to run both strobe and count parallely (claude soln 1)

for i in range (0, 60, 1):
    count_intensity = 0
    while user_switch.value() == 0: #logic1
        count_intensity += 1 
        #start = time.ticks_ms() #logic2
    #end = time.ticks_ms()
    #count_intensity = time.ticks_diff(end, start)
    print(count_intensity)
    print(i)
    user_oiia.append(count_intensity)
    time.sleep(1)
    
#async def intensity_task(): claude soln 2
#    count_intensity = 0
#    while user_switch.value() == 0:
#        count_intensity += 1
#        user_oiia.append(count_intensity)
#        await asyncio.sleep(0)     # yield control to other tasks

#async def main():
#    await asyncio.gather(strobe_task(), intensity_task())

#asyncio.run(main())

#if len(user_oiia) == len(og_oiia): #does this need to be there?
for i in range(len(og_oiia)-1, 1):
    if (user_oiia[i] == og_oiia[i]):
        correct_responses += 1
    else:
        humanerror_count += 1
correct_responses += (humanerror_count * error_cushion) #human error / deflection sort of evened out?
percentage = ((correct_responses/len(og_oiia)) *100) # calculates percentage score
print(percentage)
#else:
 #   print('invalid attempt')