class Test:
    def __init__(self, SERVO_PIN1, angle1, max_angle1, min_angle, delay):
        self.angle1 = angle1
        self.max_angle1 = max_angle1
        self.min_angle = min_angle
        self.SERVO_PIN1 = SERVO_PIN1
        self.delay = delay
    
    def set_angle(self, a, SERVO_PIN1=None):
        if SERVO_PIN1 is None:
            SERVO_PIN1 = self.SERVO_PIN1
        pulse_width = 500 + (a/self.max_angle1) * 2000
        self.angle1 = max(self.min_angle, min(a, self.max_angle1))
        pi.set_servo_pulsewidth(SERVO_PIN1, pulse_width)
    
    def movement(self, reverse):
        global stop, run
        run = True
        stop = False
        if not reverse:
            time_a = self.max_angle1 - self.angle1
        else:
            time_a = self.angle1 - self.min_angle

        for i in range(time_a):
            if stop: break
            if not reverse:
                self.angle1 += 1
            else:
                self.angle1 -= 1
            self.set_angle(self.angle1)
            time.sleep(self.delay)
        run = False
        
    def up(self):
        self.movement(True)

    def down(self):
        self.movement(False)


# --- Create class list (same as Arduino) ---
classList = [
    Test(14, 0, 150, 0, 0.08),
    Test(15, 0, 150, 0, 0.08),
    Test(16, 0, 150, 0, 0.08),
]
