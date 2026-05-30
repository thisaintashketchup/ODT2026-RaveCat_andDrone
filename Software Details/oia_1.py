#oiaaaaaaaa
import time
from machine import Pin, PWM
import asyncio
import _thread
import random
import bluetooth
user_switch = Pin(25, Pin.IN, Pin.PULL_UP)
strobe = PWM(Pin(26, Pin.OUT))
strobe.freq(1000)
og_oiia = [1455, 1770, 1433, 1465, 1500, 1500, 771, 700, 700, 600, 1700, 1000, 1400, 1300, 1500, 1300, 1500, 1400, 1300, 1500, 1200, 1400, 1300, 1400, 1100, 1600, 1200, 1500] #oiia og moving list
user_oiia = []
count_intensity = 0
correct_responses = 0
error_cushion = 0.3
humanerror_count = 0

value = 0
name = "ESP32-stucky" #Name of Your ESP32 (Change it to avoid Confusion)

ble = bluetooth.BLE()
ble.active(False)
time.sleep(0.5)
ble.active(True)
ble.config(gap_name=name)

SERVICE_UUID = bluetooth.UUID("6e400001-b5a3-f393-e0a9-e50e24dcca9e")
CHAR_UUID = bluetooth.UUID("6e400002-b5a3-f393-e0a9-e50e24dcca9e")

CHAR = (CHAR_UUID, bluetooth.FLAG_WRITE)
SERVICE = (SERVICE_UUID, (CHAR,),)
((char_handle,),) = ble.gatts_register_services((SERVICE,))

connections = set()

def irq(event, data):
    global connections
    if event == 1:
        conn_handle, addr_type, addr = data
        connections.add(conn_handle)
        print("Connected")
        
    elif event == 2:
        conn_handle, addr_type, addr = data
        connections.discard(conn_handle)
        print("Disconnected")
        advertise(name)
        
    elif event == 3:
        conn_handle, value_handle = data
        if value_handle == char_handle:
            msg = ble.gatts_read(char_handle).decode().strip() #reading the Value written on characteristics by Phone/client
            print("Received:", msg)
                
            global value
            value = msg[0]
     

            
ble.irq(irq)

def advertise(l_name):
    
    name_bytes = l_name.encode()

    flags = bytearray([0x02, 0x01, 0x06])
    short_name = bytearray([len(name_bytes) + 1, 0x08]) + name_bytes
    full_name = bytearray([len(name_bytes) + 1, 0x09]) + name_bytes
    adv_data = flags + short_name + full_name

    ble.gap_advertise(50, adv_data=adv_data)
    print("Advertising as:", l_name)

advertise(name)
print("Waiting for connection...")

while True:
    if value == '1':
        def strobe_task(): # CLAUDE SOLN 1
            for i in range (0, 10000000, 1): # strobe light on pwm with original oiia movements.
                strobe.duty((random.randint(20,1020)))
                time.sleep(0.2)
        
#async def strobe_task(): claude soln 2
#    for val in og_oiia:
#        strobe.duty(val * 600)
#        await asyncio.sleep(0.2)

        _thread.start_new_thread(strobe_task, ()) #needed to run both strobe and count parallely (claude soln 1)
        start = -1
        for i in range (0, 60, 1):
            count_intensity = 0
            while user_switch.value() == 0: #logic1
#                 count_intensity += 1 
                start = time.ticks_ms() #logic2
            if(start>=0):
                end = time.ticks_ms()
                count_intensity = time.ticks_diff(end, start)
            print(count_intensity)
            print("seconds elapsed:" + i)
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
        for i in range(min(len(og_oiia), len(user_oiia))): #fixed by claude.  og: for i in range(len(og_oiia)-1, 1):
            diff = abs(og_oiia[i] - user_oiia[i])
            if (diff == 0):
                correct_responses += 1
            elif diff >= 10 and diff < 100:#need to figure out this error spectrum            
                humanerror_count += 5
            elif diff >= 100 and diff < 1000:
                humanerror_count += 50
            elif diff >= 1000 and diff < 10000:
                humanerror_count += 500
            else:
                humanerror_count += 5000
        correct_responses += (humanerror_count * error_cushion) #human error / deflection sort of evened out?
        percentage = ((correct_responses/len(og_oiia)) *100) # calculates percentage score
        print(percentage)
#else:
 #   print('invalid attempt')
        value = 0


