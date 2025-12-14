from Arm_Lib import Arm_Device
import time

Arm = Arm_Device()
time.sleep(0.2)

print("Moving arm to straight-up pose...")

# base, shoulder, elbow, wrist pitch, wrist roll, gripper
Arm.Arm_serial_servo_write6(
    90,   # S1: Base centered
    20,   # S2: Shoulder raised upward
    160,  # S3: Elbow straightening
    90,   # S4: Wrist pitch neutral
    90,   # S5: Wrist roll neutral
    90,   # S6: Gripper neutral
    1500  # Move in 1.5s
)

time.sleep(2)
print("Done!")
del Arm
