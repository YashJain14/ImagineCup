import cv2
import numpy as np
import pyautogui

def click_event(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f'Coordinates: X: {x}, Y: {y}')
        cv2.circle(img, (x, y), 3, (0, 0, 255), -1)
        label = input("Enter label for this point: ")
        cv2.putText(img, label, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        cv2.imshow('image', img)

# Capture screenshot
screenshot = pyautogui.screenshot()
img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

# Display the image
cv2.imshow('image', img)

# Set mouse callback function
cv2.setMouseCallback('image', click_event)

# Wait for a key event indefinitely
cv2.waitKey(0)

# Close all windows
cv2.destroyAllWindows()