import machine
import ssd1306
import time
from machine import Pin
from machine import ADC

#####################################################
### Pin configurations
#####################################################
i2c_sda = machine.Pin(3)
i2c_scl = machine.Pin(4)
button = machine.Pin(1, machine.Pin.IN, machine.Pin.PULL_UP)
pwm_pin = machine.Pin(2)
tacho_pin = machine.Pin(0, machine.Pin.IN)
#tacho_ADC = ADC(0)
#####################################################

#####################################################
### Hardware, variables Init
#####################################################
# Display
i2c = machine.I2C(sda=i2c_sda, scl=i2c_scl)
display = ssd1306.SSD1306_I2C(128, 64, i2c)

# PWM-related
last_timestamp = time.ticks_ms()
cnt = 8
pwm_duty = 90
pwm = machine.PWM(pwm_pin, freq=25000, duty_u16=int(pwm_duty*655))
pwm.init()

# Tacho-related
tacho_cnt = 0
tacho_cnt_start = 0
tacho_rpm_est = 0
#####################################################

#####################################################
### Functions
#####################################################

# PWM Update
def pwm_update(pwm, pwm_duty_percent):
    pwm.duty_u16(int(pwm_duty * 655))
    
# Push-button Interrupt
def button_handler(pin):
    global last_timestamp
    global cnt
    global pwm_duty
    
    if(time.ticks_ms() - last_timestamp > 100):        
        last_timestamp = time.ticks_ms()
        cnt += 1
        pwm_duty = (cnt % 9) * 10 + 10
        pwm_update(pwm, pwm_duty)
    else:
        return 

button.irq(trigger=machine.Pin.IRQ_FALLING, handler=button_handler)

# Tacho counter Interrupt.
# Too bad ESP32-C3 does not have a pulse counter. I guess this interrupt routine may struggle on a high-RPM fan..
def tacho_handler(pin):
    global tacho_cnt, tacho_cnt_start, tacho_rpm_est
    tacho_cnt+=1
    
    timestamp = time.ticks_ms()
    if(timestamp > tacho_cnt_start + 1000 or timestamp < tacho_cnt_start):
        tacho_cnt_start = timestamp
        tacho_rpm_est = tacho_cnt * 30 #two falling edges per a cycle
        tacho_cnt = 0

tacho_pin.irq(trigger=machine.Pin.IRQ_FALLING, handler=tacho_handler)

#####################################################


#####################################################
### Main loop
#####################################################
#print("Entering Main loop")
while True:
    display.fill(0)
    display.text('PWM Duty:' + str(pwm_duty) + "%", 0, 0)
    display.text('RPM:' + str(tacho_rpm_est) , 0, 10)
    #display.text('_'+ str(tacho_ADC.read_uv()),0,10)
    display.show()
    time.sleep(0.1)
#####################################################
