from Arm_Lib import Arm_Device
import time

# No port argument — driver must auto-detect
Arm = Arm_Device()

time.sleep(0.3)

print("Turning on WHITE")
Arm.Arm_RGB_set(255, 80, 80)
time.sleep(1)

print("Turning on RED")
Arm.Arm_RGB_set(250, 0, 0)
time.sleep(1)

print("Turning on BLUE")
Arm.Arm_RGB_set(0, 0, 50)
time.sleep(1)

print("Turning on YELLOW")
Arm.Arm_RGB_set(255, 80, 0)
time.sleep(1)

print("Turning on GREEN")
Arm.Arm_RGB_set(0, 50, 0)
time.sleep(1)

print("Done!")
del Arm
