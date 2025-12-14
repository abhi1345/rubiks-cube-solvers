from Arm_Lib import Arm_Device
import time

Arm = Arm_Device()
time.sleep(0.2)

print("Trying to move servo 1...")
Arm.Arm_serial_servo_write(1, 120, 1000)
time.sleep(2)

Arm.Arm_serial_servo_write(1, 60, 1000)
time.sleep(2)

Arm.Arm_serial_servo_write(1, 90, 1000)
time.sleep(2)

print("Done.")
del Arm
