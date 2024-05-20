import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from ultralytics import YOLO
import cv2
from datetime import datetime
import customtkinter
import subprocess
import sys
import os

# Load YOLOv8 model
model = YOLO('yolov8n.pt')

# Location
video_path = './langvideo.mp4'
cap = cv2.VideoCapture(video_path)
location = "Molde"

# Define lists for dropdown options
object_options = ["airplane", "bird", "car", "drone", "frisbee"]
location_options = ["Molde", "Stokke", "Leknes", "Røst", "Vardø", "Harsvik"]

def main_screen():
    def banner(app):
        banner_label = customtkinter.CTkLabel(inner_frame, text="Object Detection Program", font=("Inter", 33, "italic"), text_color="GREEN")
        banner_label.grid(row=0, column=0, padx=25, pady=20, sticky="w")



        separator = ttk.Separator(inner_frame, orient="horizontal")
        separator.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=10)

        def history_button_click():
            open_history_screen()

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
            height, width, _ = frame.shape
            cropped_frame = frame[height // 5:1 * height // 2, width // 7:4 * width // 5]

            results = model.track(cropped_frame, conf=0.75, persist=True)
            frame_ = results[0].plot()

            for box in results[0].boxes:
                class_id = int(box.cls)
                class_label = results[0].names[class_id]
                current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"{current_time}_{class_label}_{location}.jpg"
                cv2.imwrite(filename, frame_)
                print(f"Saved image: {filename}")

            img = cv2.cvtColor(frame_, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img = img.resize((640, 480), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)

            video_label.img = img
            video_label.config(image=img)

            inner_frame.after(25, update_video_feed, inner_frame)

    def video(inner_frame):
        video_frame = ttk.Frame(inner_frame)
        video_frame.grid(row=2, column=0, columnspan=3, padx=20, pady=20, sticky="w")

        global video_label
        video_label = tk.Label(video_frame)
        video_label.grid(row=0, column=0)

        update_video_feed(inner_frame)

    def main():
        global app, canvas, inner_frame

        app = customtkinter.CTk()
        app.geometry("620x560")
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

def history_screen():
    def edit_filename(image_file, button, object_var, location_var, reload_ui):
        # Extract information from file name
        file_name = os.path.splitext(image_file)[0]
        info = file_name.split("_")
        current_object = info[2]
        current_date = info[0]
        current_time = info[1]
        current_location = info[3]

        # Create a dialog window
        dialog = tk.Toplevel()
        dialog.title("Edit Filename")
        dialog.geometry("420x390")

        object_label = customtkinter.CTkLabel(dialog, text="Object: ", font=("Inter", 18, "bold"),
                                              text_color="black")
        object_label.pack()
        object_menu = customtkinter.CTkOptionMenu(dialog, values=object_options, variable=object_var)
        object_menu.set(current_object)
        object_menu.pack()

        YearMonthDay_label = customtkinter.CTkLabel(dialog, text="Year-Month-Day: ", font=("Inter", 18, "bold"),
                                                    text_color="black")
        YearMonthDay_label.pack()
        entry = customtkinter.CTkTextbox(dialog, height=1, width=120)
        entry.insert("1.0", current_date)
        entry.configure(state="disabled")
        entry.pack()

        time_label = customtkinter.CTkLabel(dialog, text="hour-minute-second: ", font=("Inter", 18, "bold"),
                                            text_color="black")
        time_label.pack()
        time_entry = customtkinter.CTkTextbox(dialog, height=1, width=120)
        time_entry.insert("1.0", current_time)
        time_entry.configure(state="disabled")
        time_entry.pack()

        location_label = customtkinter.CTkLabel(dialog, text="Location: ", font=("Inter", 18, "bold"),
                                                text_color="black")
        location_label.pack()
        location_entry = customtkinter.CTkTextbox(dialog, height=1, width=120)
        location_entry.insert("1.0", current_location)
        location_entry.configure(state="disabled")
        location_entry.pack()

        # Function to update the filename and button text
        def update_filename():
            new_object = object_var.get()
            new_date = entry.get("1.0", "end-1c")
            new_time = time_entry.get("1.0", "end-1c")
            new_location = location_var.get()

            if new_date and new_time:
                # Construct the new filename
                new_filename = f"{new_date}_{new_time}_{new_object}_{new_location}.jpg"
                new_filepath = os.path.join(".", new_filename)
                if os.path.exists(new_filepath):
                    # Show a message if the new filename already exists
                    messagebox.showerror("Error", "A file with this name already exists.")
                else:
                    # Rename the file
                    os.rename(image_file, new_filepath)
                    # Update the button text with the new information
                    button.configure(text=f"Object: {new_object}\nDate: {new_filename}\nLocation: {new_location}")
                    # Close the dialog window
                    dialog.destroy()
                    # Reload UI
                    reload_ui()

        # Add OK button to confirm changes
        spacer_label = customtkinter.CTkLabel(dialog, text="  ", font=("Inter", 18, "bold"),
                                              text_color="black")
        spacer_label.pack()
        apply_change_button = customtkinter.CTkButton(dialog, text="Apply Change", command=update_filename,
                                                      text_color="white", font=("inter", 14, "bold"), fg_color="Green",
                                                      anchor="w")
        apply_change_button.pack()

    def load_images(inner_frame, object_var, location_var, reload_ui, filtered_images=None):
        if filtered_images is None:
            # Load all images if no filter is applied
            image_files = [f for f in os.listdir(".") if f.endswith(".jpg")]
        else:
            # Use filtered images if available
            image_files = filtered_images

        for i, image_file in enumerate(image_files):
            # Load image
            image_path = os.path.join(".", image_file)
            image = Image.open(image_path)

            # Convert PIL.Image to CTkImage
            ctk_image = customtkinter.CTkImage(image, size=(190, 150))
            # Extract information from file name
            file_name = os.path.splitext(image_file)[0]
            info = file_name.split("_")
            object_name = info[2]
            date = info[0]
            time = info[1]
            location = info[3]

            # Create button to display information and image
            button_text = (f"Object: {object_name}               Date: {date}"
                           f"\n\n\nLocation: {location}          Time: {time}")
            button = customtkinter.CTkButton(inner_frame, text=button_text, compound="left", image=ctk_image,
                                             text_color="black",
                                             font=("inter", 14, "bold"), fg_color="gray89")

            # Define function to edit filename
            def edit_file(image_file=image_file):
                edit_filename(image_file, button, object_var, location_var, reload_ui)

            button.configure(command=edit_file)
            button.configure(width=325)
            button.grid(row=i + 4, column=0, padx=20, pady=10)

        # Configure inner frame to resize properly
        inner_frame.update_idletasks()
        inner_frame.config(width=inner_frame.winfo_reqwidth())

    def reload_ui(filtered_images=None):
        # Destroy all widgets in the inner_frame
        for widget in inner_frame.winfo_children():
            widget.destroy()

        # Reload the UI elements
        banner(app)
        filter_button()
        stats()
        load_images(inner_frame, object_var, location_var, reload_ui, filtered_images)

        # Update the canvas scroll region
        inner_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def filter_button():

        button_text = (f"Filters ")
        button = customtkinter.CTkButton(inner_frame, text=button_text, compound="left",
                                         text_color="white",
                                         font=("inter", 14, "bold"), fg_color="Green", anchor="w")
        button.configure(width=280)
        button.grid(row=3, column=0, padx=25, pady=0, sticky="w")

        def apply_filter():
            selected_locations = [location_options[i] for i, var in enumerate(location_vars) if var.get()]
            selected_objects = [object_options[i] for i, var in enumerate(object_vars) if var.get()]
            date_range = (start_date_var.get(), end_date_var.get())

            # Reload UI with filtered images
            reload_ui(filtered_images=get_filtered_images(selected_locations, selected_objects, date_range))

        # Create a filter window only if it's the first time
        def filter_window():
            global filter_window, location_vars, object_vars, start_date_var, end_date_var

            filter_window = tk.Toplevel()
            filter_window.title("Apply Filters")
            filter_window.geometry("300x600")

            location_vars = []
            object_vars = []

            # Add checkboxes for locations
            location_label = customtkinter.CTkLabel(filter_window, text="Location", font=("Inter", 22, "bold"),
                                                    text_color="black")
            location_label.pack()
            for location_option in location_options:
                var = tk.BooleanVar()
                location_vars.append(var)
                checkbox = customtkinter.CTkCheckBox(filter_window, text=location_option, variable=var)
                checkbox.pack(ipady=5)

            # Add checkboxes for objects
            object_label = customtkinter.CTkLabel(filter_window, text="Object", font=("Inter", 22, "bold"),
                                                  text_color="black")
            object_label.pack()
            for object_option in object_options:
                var = tk.BooleanVar()
                object_vars.append(var)
                checkbox = customtkinter.CTkCheckBox(filter_window, text=object_option, variable=var)
                checkbox.pack(ipady=5)

            # Add date range filter
            date_label = customtkinter.CTkLabel(filter_window, text="Date Range", font=("Inter", 22, "bold"),
                                                text_color="black")
            date_label.pack()

            start_date_label = customtkinter.CTkLabel(filter_window, text="Start Date (YYYYMMDD):", font=("Inter", 16),
                                                      text_color="black")
            start_date_label.pack()
            start_date_var = tk.StringVar()
            start_date_entry = customtkinter.CTkEntry(filter_window, textvariable=start_date_var)
            start_date_entry.pack()

            end_date_label = customtkinter.CTkLabel(filter_window, text="End Date (YYYYMMDD):", font=("Inter", 16),
                                                    text_color="black")
            end_date_label.pack()
            end_date_var = tk.StringVar()
            end_date_entry = customtkinter.CTkEntry(filter_window, textvariable=end_date_var)
            end_date_entry.pack()

            # Add apply button
            button1 = customtkinter.CTkButton(filter_window, text="Apply Filter", command=apply_filter,
                                              text_color="white", font=("inter", 14, "bold"), fg_color="Green",
                                              anchor="w")
            button1.pack()

        # Opens Filter_window
        button.configure(command=filter_window)

    def get_filtered_images(selected_locations, selected_objects, date_range):
        filtered_images = []
        start_date, end_date = date_range

        for image_file in os.listdir("."):
            if image_file.endswith(".jpg"):
                file_name = os.path.splitext(image_file)[0]
                info = file_name.split("_")
                date = info[0]  # 'YYYY-MM-DD'
                time = info[1]  # 'HH-MM-SS'
                object_name = info[2]
                location = info[3]

                # Convert date and time to datetime object for comparison
                image_date = datetime.strptime(date + "_" + time, "%Y-%m-%d_%H-%M-%S")

                # Filter by selected locations, objects, and date range
                if (not selected_locations or location in selected_locations) and \
                        (not selected_objects or object_name in selected_objects) and \
                        (not start_date or image_date >= datetime.strptime(start_date, "%Y-%m-%d")) and \
                        (not end_date or image_date <= datetime.strptime(end_date, "%Y-%m-%d")):
                    filtered_images.append((image_date, image_file))

        # Sort images by date in descending order
        filtered_images.sort(key=lambda x: x[0], reverse=True)

        # Return the filenames of the sorted images
        return [image_file for _, image_file in filtered_images]

    def stats():
        object_counts = {obj: 0 for obj in object_options}
        total_objects = 0

        for image_file in os.listdir("."):
            if image_file.endswith(".jpg"):
                file_name = os.path.splitext(image_file)[0]
                info = file_name.split("_")
                object_name = info[2]
                object_counts[object_name] += 1
                total_objects += 1

        button_text = "Stats:\n"
        for obj, count in object_counts.items():
            button_text += f"{obj.capitalize()} Detected: {count}\n"
        button_text += f"\nTotal objects: {total_objects}"

        button = customtkinter.CTkButton(inner_frame, text=button_text,
                                        text_color="black",
                                        font=("inter", 14, "bold"), fg_color="gray89")
        button.configure(width=200)
        button.grid(row=4, column=1, padx=20, pady=10)

    def banner(app):
        banner_label = customtkinter.CTkLabel(inner_frame, text="Object Detection Program", font=("Inter", 33, "italic"), text_color="GREEN")
        banner_label.grid(row=0, column=0, padx=25, pady=20, sticky="w")

        history_label = customtkinter.CTkLabel(inner_frame, text="History", font=("Inter", 33, "bold"), text_color="black")
        history_label.grid(row=1, column=0, padx=25, pady=10, sticky="w")

        separator = ttk.Separator(inner_frame, orient="horizontal")
        separator.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=10)

        def home_button_click():
            open_main_screen()

        button_text = (f"Home")
        button = customtkinter.CTkButton(inner_frame, text=button_text,
                                        text_color="white",
                                        font=("inter", 14, "bold"), fg_color="GREEN",
                                        command=home_button_click)
        button.configure(width=150)
        button.grid(row=0, column=1, padx=10, pady=10)

    def main():
        global app, canvas, inner_frame, object_var, location_var

        app = customtkinter.CTk()
        app.geometry("820x680")
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

        object_var = tk.StringVar(value=object_options[0])
        location_var = tk.StringVar(value=location_options[0])

        inner_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        banner(app)
        filter_button()
        stats()
        load_images(inner_frame, object_var, location_var, reload_ui)

        app.mainloop()

    if __name__ == "__main__":
        main()

def open_main_screen():
    global app
    try:
        app.destroy()
    except:
        pass
    main_screen()

def open_history_screen():
    global app
    try:
        app.destroy()
    except:
        pass
    history_screen()

if __name__ == "__main__":
    open_main_screen()
