import cv2
import tkinter as tk
from tkinter import messagebox

def capture_images_with_rectangle():
    # Open the default camera (index 0)
    cap = cv2.VideoCapture(0)

    # Check if the camera is opened successfully
    if not cap.isOpened():
        print("Error: Unable to access the camera.")
        return

    # Counter for capturing multiple images
    slip_count = 0

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Create a Tkinter root window (hidden)
    root = tk.Tk()
    root.withdraw()

    # Variable to track the 'v' key state
    v_key_pressed = False

    # Loop to continuously read frames from the camera and display them
    while True:
        # Read a frame from the camera
        ret, frame = cap.read()

        # Check if the frame was read successfully
        if not ret:
            print("Error: Unable to read frame from the camera.")
            break

        # Convert frame to grayscale for slip detection
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect slip in the frame
        slips = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # Draw green rectangle around detected slips
        for (x, y, w, h) in slips:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Display the frame
        cv2.imshow('Camera', frame)

        # Capture an image when 'c' is pressed
        if cv2.waitKey(1) & 0xFF == ord('c'):
            # Save the captured image to a file with a unique filename
            slip_count += 1
            slip_filename = f'captured_PDF_{slip_count}.jpg'
            cv2.imwrite(slip_filename, frame)
            print(f"Image captured and saved as '{slip_filename}'")

             # Notify the user with a pop-up message
            messagebox.showinfo("Image Captured", f"Image captured and saved as '{slip_filename}'")

        # Click the 'v' key to exit the modal box
        key = cv2.waitKey(1) & 0xFF
        if key == ord('v') and not v_key_pressed:
            response = messagebox.askokcancel("Exit Confirmation", "Are you sure you want to exit?")
            if response:
                break
            else:
                v_key_pressed = True
        elif key != ord('v'):
            v_key_pressed = False

    # Release the camera and close the window
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Call the function to access the camera and capture images
    capture_images_with_rectangle()