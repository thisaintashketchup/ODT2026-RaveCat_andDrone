from machine import I2C, Pin, PWM
import time
import bluetooth
##########Claude Fixed Code############################################################################
class MPU6500:
    def setup(self, i2c, addr=0x68): ##FIXED: setup->setup so class can be instantiated normally
        self.i2c= i2c
        self.addr= addr
        self.i2c.writeto_mem(self.addr, 0x6B, b'\x00')
        self.i2c.writeto_mem(self.addr, 0x1B, b'\x10')
        self.i2c.writeto_mem(self.addr, 0x1C, b'\x10')
    def readraw(self, reg, n=6):
        data = self.i2c.readfrom_mem(self.addr, reg, n)
        vals = []
        for i in range(0, n, 2):
            v = (data[i] << 8) | data[i+1]
            if v & 0x8000:
                v -=65536
            vals.append(v)
        return vals
    def acceleration(self):
        x, y, z = self.readraw(0x3B, 6)
        return (x, y, z)
    def gyro(self):
        x, y, z = self.readraw(0x43, 6) ##FIXED: was 'x, y, y, z' (duplicate y, missing z), unpacking 3 values into 4 variables would crash
        return (x, y, z)
##########################################################################################################
class PID:
    def setup(self, Kp, Ki, Kd, setpoint=0.0): ##FIXED: setup->setup
        self.Kp= Kp
        self.Ki= Ki
        self.Kd= Kd
        self.setpoint = setpoint
        self.preverror = 0.0
        self.integ = 0.0
        self.prevtime = time.ticks_ms()
    def update(self, measurement):
        now= time.ticks_ms()
        dt_ms = time.ticks_diff(now, self.prevtime)
        if dt_ms <= 0:
            dt_ms = 1
        dt = dt_ms / 1000.0

        error= self.setpoint - measurement
        self.integ += error * dt
        derivative= (error -self.preverror) / dt

        output= (self.Kp*error
            +self.Ki*self.integ
            +self.Kd*derivative) ##FIXED: 'output=' alone on a line is a SyntaxError; moved opening parenthesis to same line
        
        self.preverror =error
        self.prevtime =now

        return output
###################yayyy#####:3#####################################################
        
class FilterGnA:
    def setup(self, alpha=0.95): ##FIXED: setup->setup
        self.alpha = alpha
        self.roll =0.0
        self.pitch =0.0
        self.yaw =0.0
    def update(self,ax,ay,az,gx,gy,gz,dt):
        if az != 0: 
            accelr= -ay/az 
            accelp= ax/az
        else:
            accelr, accelp = 0.0, 0.0
        ##FIXED: removed 3 lines that pre-integrated gyro (self.roll += gx*dt etc.) before the complementary filter line, causing double integration
        self.roll =self.alpha * (self.roll + gx * dt) + (1.0 -self.alpha) * accelr
        self.pitch =self.alpha * (self.pitch + gy * dt) + (1.0 -self.alpha) * accelp
        self.yaw += gz*dt ##yaw has no accel correction so single integration is correct

        return self.roll, self.pitch, self.yaw

class Motors:
    def setup(self, pins=(25,26), freq=400): ##FIXED: setup->setup
        self.pwms =[PWM(Pin(z, Pin.OUT), frequency=freq) for z in pins]
        self.armed =False
        self.throttle =0.0
        self.corrections =(0.0,0.0,0.0)
    def arm(self):
        self.armed= True
        minimus= 1000
        for pwm in self.pwms:
            pwm.duty_u16(self.PWMconvert(minimus))
    def disarm(self):
        self.armed= False ##FIXED: was 'self.disarmed = False', wrong attribute name, also logic was inverted
        down= 0
        for pwm in self.pwms:
            pwm.duty_u16(self.PWMconvert(down))
    def PWMconvert(self, us): ##FIXED: 'cycle= 20,000' was a tuple (20,0) not 20000; also 'minimus' was referenced but not in scope here, now uses the 'us' parameter correctly
        cycle= 20000
        return int((us/cycle) * 65535)
    def mixy(self, throttle, roll, pitch, yaw):
        if not self.armed:
            return
        minimus =1000
        maximus =2000
        midimus =1500
        pulse = minimus + (maximus-minimus)* throttle
        
        fr = pulse + roll - pitch + yaw
        fl = pulse - roll - pitch - yaw
        bl = pulse - roll + pitch + yaw
        br = pulse + roll + pitch - yaw
        
        pulses = [fr, fl, bl, br]
        for i, pwm in enumerate(self.pwms):
            pwm.duty_u16(self.PWMconvert(pulses[i]))
#############################################################<3############
i2c = I2C(scl=Pin(22),
    sda= Pin(21),
    freq= 400_000)
sensor = MPU6500(i2c)
cf = FilterGnA(alpha=0.95)

pid_roll= PID(Kp=0.05, Ki=0.001, Kd=0.005, setpoint=0.0)
pid_pitch= PID(Kp=0.05, Ki=0.001, Kd=0.005, setpoint=0.0)
pid_yaw= PID(Kp=0.03, Ki=0.0005, Kd=0.003, setpoint=0.0)

motors = Motors(freq=400)

def calibrate_gyro():
    gx_sum= 0
    gy_sum= 0
    gz_sum= 0 

    for _ in range(300):
        gx, gy, gz = sensor.gyro()
        gx_sum += gx
        gy_sum += gy
        gz_sum += gz
        time.sleep_ms(10)
    print("gx =", gx, "gy =", gy, "gz =", gz)
    return gx_sum / 300.0, gy_sum / 300.0, gz_sum / 300.0

def in_safe_zone(angle, max_angle_deg=40): # if tilted beyond 20 degrees, disarm or reduce throttle
    deg_per_unit = 10  # rough scaling for raw angle range
    return abs(angle * deg_per_unit) <= max_angle_deg #abs= |function|

#########################################################################################################

gx_off, gy_off, gz_off = calibrate_gyro()
motors.arm()
print("Calibration finished")
prev_ms = time.ticks_ms()
while True:
    now_ms = time.ticks_ms()
    dt_ms = time.ticks_diff(now_ms, prev_ms)
    if dt_ms <= 0:
        prev_ms = now_ms
        continue
    dt = dt_ms / 1000.0
    prev_ms = now_ms
    
    ax, ay, az = sensor.acceleration() # Read sensor
    gx, gy, gz = sensor.gyro()
    
    gx -= gx_off # Remove offset (simple calibration)
    gy -= gy_off
    gz -= gz_off
    # 1) get roll, pitch, yaw
    roll, pitch, yaw = cf.update(ax, ay, az, gx, gy, gz, dt)
    # 2. PID on all three axes
    corr_roll = pid_roll.update(roll) #correct
    corr_pitch = pid_pitch.update(pitch)
    corr_yaw = pid_yaw.update(yaw)
    # 3) Scale corrections
    corr_scale = 100
    corr_roll *= corr_scale
    corr_pitch *= corr_scale
    corr_yaw *= corr_scale
    # 4) Safety: throttle & tilt limits
    safe_throttle = app.throttle
    if not in_safe_zone(roll) or not in_safe_zone(pitch):
        safe_throttle = 0.0
        print ("ohno")
    # 5. Motor mixing (throttle + corrections)
    if app.throttle > 0.01:
        motors.mixy(safe_throttle, corr_roll, corr_pitch, corr_yaw) ##FIXED: motors.set() doesn't exist; renamed to motors.mixy() to match the Motors class
    time.sleep_ms(10)


