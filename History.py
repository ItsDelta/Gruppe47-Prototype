import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image
import customtkinter
import sys
import subprocess
from PIL import Image, ImageTk
from ultralytics import YOLO
import cv2
from datetime import datetime

# Define lists for dropdown options
object_options = ["airplane", "bird", "car", "drone", "frisbee"]
location_options = ["Molde", "Stokke", "Leknes", "Røst", "Vardø", "Harsvik"]

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
    object_menu = customtkinter.CTkOptionMenu(dialog,values=object_options, variable=object_var)
    object_menu.set(current_object)
    object_menu.pack()


    #ttk.Label(dialog, text="YearMonthDate:").pack()
    YearMonthDay_label = customtkinter.CTkLabel(dialog, text="Year-Month-Day: ", font=("Inter", 18, "bold"),
                                            text_color="black")
    YearMonthDay_label.pack()
    #entry = ttk.Entry(dialog)
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
    object_menu = customtkinter.CTkOptionMenu(dialog,values=location_options, variable=location_var)
    object_menu.set(current_location)
    object_menu.pack()


    # Function to update the filename and button text
    def update_filename():
        new_object = object_var.get()
        new_date = entry.get("1.0","end-1c")
        new_time = time_entry.get("1.0","end-1c")
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
    #ttk.Button(dialog, text="Apply", command=update_filename).pack()
    spacer_label = customtkinter.CTkLabel(dialog, text="  ", font=("Inter", 18, "bold"),
                                            text_color="black")
    spacer_label.pack()
    apply_change_button = customtkinter.CTkButton(dialog, text="Apply Change", command=update_filename,
                                      text_color="white", font=("inter", 14, "bold"), fg_color="Green", anchor="w")
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
        object_name = info[2] #endre 2
        date = info[0] #endre date til 0
        time = info[1] #endre time til 1
        location = info[3] #beholder 3

        # Create button to display information and image
        button_text = (f"Object: {object_name}               Date: {date}"
                       f"\n\n\nLocation: {location}          Time: {time}")
        button = customtkinter.CTkButton(inner_frame, text=button_text, compound="left", image=ctk_image, text_color="black",
                                          font=("inter", 14, "bold"), fg_color="gray89")

        # Define function to edit filename
        def edit_file(image_file=image_file):
            edit_filename(image_file, button, object_var, location_var, reload_ui)

        button.configure(command=edit_file)
        button.configure(width=325)
        button.grid(row=i+4, column=0, padx=20, pady=10)

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

        # Reload UI with filtered images
        reload_ui(filtered_images=get_filtered_images(selected_locations, selected_objects))

    # Create a filter window only if it's the first time
    def filter_window():
        global filter_window, location_vars, object_vars

        filter_window = tk.Toplevel()
        filter_window.title("Apply Filters")
        filter_window.geometry("300x545")
        #scrollable_frame = customtkinter.CTkScrollableFrame(filter_window, width=200, height=200)

        location_vars = []
        object_vars = []

        # Add checkboxes for locations
        #ttk.Label(filter_window, text="Locations:").pack()
        location_label = customtkinter.CTkLabel(filter_window, text="Location", font=("Inter", 22, "bold"),
                                               text_color="black")
        location_label.pack()
        for location_option in location_options:
            var = tk.BooleanVar()
            location_vars.append(var)
            #ttk.Checkbutton(filter_window, text=location_option, variable=var).pack()
            checkbox_1 = customtkinter.CTkCheckBox(filter_window, text=location_option, variable=var, )
            checkbox_1.pack(ipady=5)



        # Add checkboxes for objects
        #ttk.Label(filter_window, text="Objects:").pack()
        object_label = customtkinter.CTkLabel(filter_window, text="Object", font=("Inter", 22, "bold"),
                                               text_color="black")
        object_label.pack()
        for object_option in object_options:
            var = tk.BooleanVar()
            object_vars.append(var)
            #ttk.Checkbutton(filter_window, text=object_option, variable=var).pack()
            checkbox_1 = customtkinter.CTkCheckBox(filter_window, text=object_option, variable=var, )
            checkbox_1.pack(ipady=5)

        # Add apply button
        #ttk.Button(filter_window, text="Apply Filter", command=apply_filter).pack()
        button1 = customtkinter.CTkButton(filter_window, text="Apply Filter", command=apply_filter,
                                          text_color="white", font=("inter", 14, "bold"), fg_color="Green", anchor="w")
        button1.pack()

    #Opens Filter_window
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
    # Count occurrences of each object type
    object_counts = {obj: 0 for obj in object_options}
    total_objects = 0

    # Iterate over image files and count occurrences of each object type
    for image_file in os.listdir("."):
        if image_file.endswith(".jpg"):
            file_name = os.path.splitext(image_file)[0]
            info = file_name.split("_")
            object_name = info[2]
            object_counts[object_name] += 1
            total_objects += 1

    # Create the stats button text dynamically based on the object counts
    button_text = "Stats:\n"
    for obj, count in object_counts.items():
        button_text += f"{obj.capitalize()} Detected: {count}\n"
    button_text += f"\nTotal objects: {total_objects}"

    # Create the button with the dynamically generated text
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

    # Add a separator
    separator = ttk.Separator(inner_frame, orient="horizontal")
    separator.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=10)



    def home_button_click():

        # Close the main application window
        #app.destroy()
        #Launch the subprocess
        subprocess.run(["python", "mainScreen.py"])  # Replace "path_to_other_python_file.py" with the actual path
        sys.exit()

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
