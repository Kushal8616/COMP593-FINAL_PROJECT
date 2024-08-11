from tkinter import *
from tkinter import messagebox
import apod_desktop
import image_lib
from datetime import datetime
import os

# Define paths and global variables
script_dir = os.path.dirname(os.path.abspath(__file__))
image_cache_dir = os.path.join(script_dir, 'images')

def update_image():
    """Update the displayed image based on the selected date."""
    apod_date = get_apod_date()
    apod_id = apod_desktop.add_apod_to_cache(apod_date)
    apod_info = apod_desktop.get_apod_info(apod_id)
    
    if apod_info:
        img_path = apod_info['file_path']
        if os.path.exists(img_path):
            image = PhotoImage(file=img_path)
            image_label.config(image=image)
            image_label.image = image
            status_label.config(text=f"APOD for {apod_date.isoformat()}: {apod_info['title']}")
            set_background_button.config(state=NORMAL)
        else:
            messagebox.showerror("Error", "Failed to load image.")
    else:
        messagebox.showerror("Error", "Failed to retrieve APOD information.")

def set_background():
    """Set the APOD image as the desktop background."""
    apod_date = get_apod_date()
    apod_id = apod_desktop.add_apod_to_cache(apod_date)
    apod_info = apod_desktop.get_apod_info(apod_id)
    
    if apod_info:
        if image_lib.set_desktop_background_image(apod_info['file_path']):
            messagebox.showinfo("Success", "Desktop background updated successfully.")
        else:
            messagebox.showerror("Error", "Failed to set desktop background.")
    else:
        messagebox.showerror("Error", "Failed to retrieve APOD information.")

def get_apod_date():
    """Get the APOD date from the date entry field."""
    try:
        apod_date = datetime.strptime(date_entry.get(), '%Y-%m-%d').date()
        if apod_date > datetime.today().date():
            raise ValueError("Date cannot be in the future.")
        return apod_date
    except ValueError as e:
        messagebox.showerror("Error", f"Invalid date format: {e}")
        return datetime.today().date()

# Initialize the image cache
apod_desktop.init_apod_cache()

# Create the GUI
root = Tk()
root.title("APOD Viewer")
root.geometry('600x400')

# Widgets
date_label = Label(root, text="Enter APOD Date (YYYY-MM-DD):")
date_label.pack(pady=10)

date_entry = Entry(root)
date_entry.insert(0, datetime.today().strftime('%Y-%m-%d'))
date_entry.pack(pady=10)

update_button = Button(root, text="Update Image", command=update_image)
update_button.pack(pady=10)

set_background_button = Button(root, text="Set as Desktop Background", command=set_background)
set_background_button.pack(pady=10)

image_label = Label(root)
image_label.pack(pady=10)

status_label = Label(root, text="")
status_label.pack(pady=10)

root.mainloop()