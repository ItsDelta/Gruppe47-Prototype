import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from ultralytics import YOLO
import cv2
from datetime import datetime
import customtkinter
import subprocess
import sys

# Load YOLOv8 model
model = YOLO('yolov8n.pt')

# Location
video_path = './langvideo.mp4'
cap = cv2.VideoCapture(video_path)
location = "Molde"

def banner(app):
    banner_label = customtkinter.CTkLabel(inner_frame, text="Object Detection Program", font=("Inter", 33, "italic"), text_color="GREEN")
    banner_label.grid(row=0, column=0, padx=25, pady=20, sticky="w")

    # Add a separator
    separator = ttk.Separator(inner_frame, orient="horizontal")
    separator.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=10)

    def history_button_click():

        # Close the main application window
        app.destroy()
        #Launch the subprocess
        subprocess.run(["python", "History.py"])  # Replace "path_to_other_python_file.py" with the actual path
        sys.exit()

    button_text = (f"History")
    button = customtkinter.CTkButton(inner_frame, text=button_text,
                                     text_color="white",
                                     font=("inter", 14, "bold"), fg_color="GREEN",
                                     command=history_button_click)
    button.configure(width=150)
    button.grid(row=0, column=1, padx=10, pady=10)

def update_video_feed(inner_frame):
    ret, frame = cap.read()
    if ret:
        # Crop out upper and lower parts as well as sides of the frame
        height, width, _ = frame.shape
        # Define the cropping region of the frame
        cropped_frame = frame[height // 5:1 * height // 2, width // 7:4 * width // 5]

        # Detect objects and track them
        results = model.track(cropped_frame, conf=0.75, persist=True)

        # Plot results
        frame_ = results[0].plot()

        # Iterate over detected objects
        for box in results[0].boxes:
            class_id = int(box.cls)  # Get class ID
            class_label = results[0].names[class_id]  # Get class label from class ID
            print(f'Detected class: {class_label}')  # Print class label

            # Save the annotated frame with the date and time as the filename
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{current_time}_{class_label}_{location}.jpg"
            cv2.imwrite(filename, frame_)
            print(f"Saved image: {filename}")

        # Convert the frame to tkinter compatible format
        img = cv2.cvtColor(frame_, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img = img.resize((640, 480), Image.LANCZOS)
        img = ImageTk.PhotoImage(img)

        # Update the label with the new frame
        video_label.img = img
        video_label.config(image=img)

        # Call the function again after 25 milliseconds
        inner_frame.after(25, update_video_feed, inner_frame)

def video(inner_frame):
    # Create a frame to hold the video feed
    video_frame = ttk.Frame(inner_frame)
    video_frame.grid(row=2, column=0, columnspan=3, padx=20, pady=20, sticky="w")  # Adjust columnspan to 2

    # Create a label to display the video feed
    global video_label
    video_label = tk.Label(video_frame)
    video_label.grid(row=0, column=0)

    # Start updating the video feed
    update_video_feed(inner_frame)

def main():
    global app, canvas, inner_frame, object_var, location_var

    app = customtkinter.CTk()
    app.geometry("620x580")
    app.title("Object Detection Program Prototype 3.2")

    frame_1 = customtkinter.CTkFrame(master=app)
    frame_1.pack(pady=0, padx=0, fill="both", expand=True)

    canvas = tk.Canvas(frame_1)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(frame_1, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)

    inner_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    inner_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    banner(app)
    video(inner_frame)

    app.mainloop()

if __name__ == "__main__":
    main()
