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
        file_name = os.path.splitext(image_file)[0]
        info = file_name.split("_")
        current_object = info[2]
        current_date = info[0]
        current_time = info[1]
        current_location = info[3]

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
        entry.pack()

        time_label = customtkinter.CTkLabel(dialog, text="hour-minute-second: ", font=("Inter", 18, "bold"),
                                                text_color="black")
        time_label.pack()
        time_entry = customtkinter.CTkTextbox(dialog, height=1, width=120)
        time_entry.insert("1.0", current_time)
        time_entry.pack()

        location_label = customtkinter.CTkLabel(dialog, text="Location: ", font=("Inter", 18, "bold"),
                                                text_color="black")
        location_label.pack()
        object_menu = customtkinter.CTkOptionMenu(dialog, values=location_options, variable=location_var)
        object_menu.set(current_location)
        object_menu.pack()

        def update_filename():
            new_object = object_var.get()
            new_date = entry.get("1.0", "end-1c")
            new_time = time_entry.get("1.0", "end-1c")
            new_location = location_var.get()

            if new_date and new_time:
                new_filename = f"{new_date}_{new_time}_{new_object}_{new_location}.jpg"
                new_filepath = os.path.join(".", new_filename)
                if os.path.exists(new_filepath):
                    messagebox.showerror("Error", "A file with this name already exists.")
                else:
                    os.rename(image_file, new_filepath)
                    button.configure(text=f"Object: {new_object}\nDate: {new_filename}\nLocation: {new_location}")
                    dialog.destroy()
                    reload_ui()

        spacer_label = customtkinter.CTkLabel(dialog, text="  ", font=("Inter", 18, "bold"),
                                                text_color="black")
        spacer_label.pack()
        apply_change_button = customtkinter.CTkButton(dialog, text="Apply Change", command=update_filename,
                                                    text_color="white", font=("inter", 14, "bold"), fg_color="Green", anchor="w")
        apply_change_button.pack()

    def load_images(inner_frame, object_var, location_var, reload_ui, filtered_images=None):
        if filtered_images is None:
            image_files = [f for f in os.listdir(".") if f.endswith(".jpg")]
        else:
            image_files = filtered_images

        for i, image_file in enumerate(image_files):
            image_path = os.path.join(".", image_file)
            image = Image.open(image_path)
            ctk_image = customtkinter.CTkImage(image, size=(190, 150))
            file_name = os.path.splitext(image_file)[0]
            info = file_name.split("_")
            object_name = info[2]
            date = info[0]
            time = info[1]
            location = info[3]

            button_text = (f"Object: {object_name}               Date: {date}"
                        f"\n\n\nLocation: {location}          Time: {time}")
            button = customtkinter.CTkButton(inner_frame, text=button_text, compound="left", image=ctk_image, text_color="black",
                                            font=("inter", 14, "bold"), fg_color="gray89")

            def edit_file(image_file=image_file):
                edit_filename(image_file, button, object_var, location_var, reload_ui)

            button.configure(command=edit_file)
            button.configure(width=325)
            button.grid(row=i+4, column=0, padx=20, pady=10)

        inner_frame.update_idletasks()
        inner_frame.config(width=inner_frame.winfo_reqwidth())

    def reload_ui(filtered_images=None):
        for widget in inner_frame.winfo_children():
            widget.destroy()

        banner(app)
        filter_button()
        stats()
        load_images(inner_frame, object_var, location_var, reload_ui, filtered_images)

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

            reload_ui(filtered_images=get_filtered_images(selected_locations, selected_objects))

        def filter_window():
            global filter_window, location_vars, object_vars

            filter_window = tk.Toplevel()
            filter_window.title("Apply Filters")
            filter_window.geometry("300x545")

            location_vars = []
            object_vars = []

            location_label = customtkinter.CTkLabel(filter_window, text="Location", font=("Inter", 22, "bold"),
                                                    text_color="black")
            location_label.pack()
            for location_option in location_options:
                var = tk.BooleanVar()
                location_vars.append(var)
                checkbox_1 = customtkinter.CTkCheckBox(filter_window, text=location_option, variable=var, )
                checkbox_1.pack(ipady=5)

            object_label = customtkinter.CTkLabel(filter_window, text="Object", font=("Inter", 22, "bold"),
                                                    text_color="black")
            object_label.pack()
            for object_option in object_options:
                var = tk.BooleanVar()
                object_vars.append(var)
                checkbox_1 = customtkinter.CTkCheckBox(filter_window, text=object_option, variable=var, )
                checkbox_1.pack(ipady=5)

            button1 = customtkinter.CTkButton(filter_window, text="Apply Filter", command=apply_filter,
                                            text_color="white", font=("inter", 14, "bold"), fg_color="Green", anchor="w")
            button1.pack()

        button.configure(command=filter_window)

    def get_filtered_images(selected_locations, selected_objects):
        filtered_images = []
        for image_file in os.listdir("."):
            if image_file.endswith(".jpg"):
                file_name = os.path.splitext(image_file)[0]
                info = file_name.split("_")
                location = info[3]
                object_name = info[0]
                if (not selected_locations or location in selected_locations) and \
                    (not selected_objects or object_name in selected_objects):
                    filtered_images.append(image_file)
        return filtered_images

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
