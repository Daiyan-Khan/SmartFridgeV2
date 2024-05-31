import RPi.GPIO as GPIO
import time

class ServoMotor:
    def __init__(self):
        self.SERVO_PIN = 17
        self.LEFT_LIMIT = 5.5
        self.RIGHT_LIMIT = 9
        self.CENTER_POSITION = 7
        self.STEP = 0.5
        self.current_position = self.CENTER_POSITION

        # Setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.SERVO_PIN, GPIO.OUT)
        self.pwm = GPIO.PWM(self.SERVO_PIN, 50)  # 50Hz frequency
        self.pwm.start(self.CENTER_POSITION)

    def move_servo(self, position):
        self.pwm.ChangeDutyCycle(position)
        time.sleep(0.5)
        self.current_position = position

    def turn_left(self):
        if self.current_position - self.STEP >= self.LEFT_LIMIT:
            new_position = self.current_position - self.STEP
            self.move_servo(new_position)
            time.sleep(0.5)
            self.pwm.ChangeDutyCycle(0)
        else:
            print("Left limit reached")

    def turn_right(self):
        if self.current_position + self.STEP <= self.RIGHT_LIMIT:
            new_position = self.current_position + self.STEP
            self.move_servo(new_position)
            time.sleep(0.5)
            self.pwm.ChangeDutyCycle(0)
        else:
            print("Right limit reached")

    def center_camera(self):
        self.move_servo(self.CENTER_POSITION)
        time.sleep(0.5)
        self.pwm.ChangeDutyCycle(0)

    def cleanup(self):
        self.pwm.stop()
        GPIO.cleanup()

if __name__ == "__main__":
    try:
        servo_motor = ServoMotor()  # Initialize at center position

        while True:
            command = input("Enter 'l' to turn left, 'r' to turn right, 'c' to center, or 'q' to quit: ").strip().lower()

            if command == 'l':
                servo_motor.turn_left()
            elif command == 'r':
                servo_motor.turn_right()
            elif command == 'c':
                servo_motor.center_camera()
            elif command == 'q':
                break
            else:
                print("Invalid command")
    finally:
        servo_motor.cleanup()

