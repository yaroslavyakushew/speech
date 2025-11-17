import pigpio
import time

SERVO_GPIO = 14

pi = pigpio.pi()
if pi.connected:
	print("POWERFULLL!!!!!!!!!!!!!")
	
def set_angle(angle):
	pulse_width = int(500 + ((angle/180.0) * 2000))
	pi.set_servo_pulsewidth(SERVO_GPIO, pulse_width)
	print(pulse_width)
	

try:
    reverse = False
    a = 0
    while True:
        for i in range(170):
            set_angle(a)
            time.sleep(0.01)
            if reverse:
                a -= 1
                if a == 0:
                    reverse = False
            else:
                a += 1
                if a == 170:
                    reverse = True
	
finally:
	pi.set_servo_pulsewidth(SERVO_GPIO, 0)
	pi.stop
