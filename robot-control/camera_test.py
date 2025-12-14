import cv2

for idx in range(3):
    print(f"Trying camera index {idx}...")
    cap = cv2.VideoCapture(idx)

    if cap.isOpened():
        print(f"SUCCESS: Camera opened at index {idx}")
        break
    else:
        cap.release()
else:
    raise Exception("Could not open any camera index (0,1,2).")

# Set resolution (optional)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    cv2.imshow(f"DOFBOT Camera (index {idx})", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
