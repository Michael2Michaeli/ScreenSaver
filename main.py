import tkinter as tk
from PIL import ImageTk, Image
import glob
import shutil
import os
from datetime import datetime
import ctypes  # Importing ctypes to interact with Windows API

# Settings
settings = {
    "queue_size": 10,  # Size of the queue, how much images in the Image file
    "start_time": "08:00",  # Start time  (HH:MM)
    "end_time": "23:50",  # End time  (HH:MM)
    "time_between_images": 10000,  # Time between images updates in (milliseconds)
    "screen_control": False  # Control screen on/off: True (turn on/off screen), False (no control)
}

# 2 Folders input=queue images, and delete images
input_dir = "C:/Users/User/Desktop/images/*"
deleted_img_dir = "C:/Users/User/Desktop/deleted images"


#chicking if the dir is existing
if not os.path.exists(deleted_img_dir):
    os.makedirs(deleted_img_dir)

#create main screen
window = tk.Tk()
window.attributes('-fullscreen', True)
window.configure(bg='black')

#deploy image
def manage_images():
    global image_files
    # Get the latest list of image files
    image_files = glob.glob(input_dir)

    # if the queue is bigger then the queue_size delete first images
    while len(image_files) > settings["queue_size"]:
        # deleting the oldest image
        old_image = image_files.pop(0)
        try:
            print(f"Moving {old_image} to {deleted_img_dir}")
            # Move the image to the deleted images directory
            shutil.move(old_image, deleted_img_dir)
            # Confirm move
            print(f"Successfully moved {old_image} to {deleted_img_dir}")
        except Exception as e:
            # Print any errors that occur
            print(f"Error moving file: {old_image}. Error: {e}")


# function to load images
def load_images():
    global images, dates
    images = []
    dates = []
    for file in image_files:
        img = Image.open(file)

        # get filename and data
        filename = os.path.basename(file)
        date_str = filename.split(' at ')[0].split(' ')[-1]
        dates.append(date_str)

        # Get original image size
        img_width, img_height = img.size

        # calculate aspect ratios
        aspect_ratio = img_width / img_height
        screen_aspect_ratio = screen_width / screen_height

        # resize based on the aspect ratio
        if aspect_ratio > screen_aspect_ratio:  # Image is wider than the screen
            new_width = screen_width
            new_height = int(screen_width / aspect_ratio)
        else:  # Image is taller or same aspect ratio as the screen
            new_height = screen_height
            new_width = int(screen_height * aspect_ratio)

        # resize image
        img = img.resize((new_width, new_height), Image.LANCZOS)
        images.append(ImageTk.PhotoImage(img))


# screen width and height
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()


# Load images for the first time
manage_images()
load_images()

# Create a label to display the image
label = tk.Label(window, bg='black')  # Initialize label with black background
label.pack(expand=True)

# Create a label for the date
date_label = tk.Label(window, bg='black', fg='white', font=('Arial', 24))
date_label.pack(side='top', anchor='ne')  # Place it in the top right corner

# Create a label for the image index
index_label = tk.Label(window, bg='black', fg='white', font=('Arial', 20))
index_label.pack(side='bottom', anchor='se')  # Place it in the bottom right corner


# Function to check time zone to display
def is_within_time_range(start_time, end_time):
    now = datetime.now().time()
    return start_time <= now <= end_time


# Define the time range for the screensaver to run
start_time = datetime.strptime(settings["start_time"], "%H:%M").time()
end_time = datetime.strptime(settings["end_time"], "%H:%M").time()

# Function to turn off the screen
def turn_off_screen():
    if settings["screen_control"]:
        ctypes.windll.user32.SendMessageW(0xFFFF, 0x112, 0xF170, 2)  # Turn off the display


# Function to turn on the screen
def turn_on_screen():
    if settings["screen_control"]:
        ctypes.windll.user32.SendMessageW(0xFFFF, 0x112, 0xF170, -1)  # Turn on the display

index = 0

# Function to update the images
def update_image():
    global index

    # Check if current time, if it in time zone
    if is_within_time_range(start_time, end_time):
        # counter for the 5/200 in the bottom right
        index = (index + 1) % len(images)

        # Update date and index labels
        date_label.config(text=dates[index])  # Update date label with current image date
        index_label.config(text=f"{index + 1}/{len(images)}")  # Update index label

        # Switch to the next image
        label.config(image=images[index])  # Change to next image
        label.place(relx=0.5, rely=0.5, anchor='center')  # Center the image
    else:
        # Show black screen when its not in the time zone
        label.config(image='', bg='black')
        date_label.config(text='')
        index_label.config(text='')

    window.after(settings["time_between_images"], update_image)  # Schedule the next update


# Function to show the index of the image for the 5/200 bottom right
def show_image():
    if images:
        label.config(image=images[index])
        date_label.config(text=dates[index])
        index_label.config(text=f"{index + 1}/{len(images)}")
        label.place(relx=0.5, rely=0.5, anchor='center')


# Function for keyboard events
def key_handler(event):
    global index
    # Move to the next image
    if event.keysym == 'Right':
        index = (index + 1) % len(images)
        show_image()
    # Move to the previous image
    elif event.keysym == 'Left':
        index = (index - 1) % len(images)
        show_image()
    # delete image and move it folder
    elif event.keysym == 'Up':
        if images:
            # img file path
            old_image = image_files[index]
            try:
                print(f"Moving {old_image} to {deleted_img_dir}")
                # Move the image to the deleted images file
                shutil.move(old_image, deleted_img_dir)
                # Confirm move
                print(f"Successfully moved {old_image} to {deleted_img_dir}")
                # Remove the image from the images and dates lists
                images.pop(index)
                dates.pop(index)

                # Adjust index if necessary
                if index >= len(images):
                    index = 0
                # Update to show the new current image
                show_image()
            except Exception as e:
                #print error
                print(f"Error moving file: {old_image}. Error: {e}")


# Bind the key handler to the window
window.bind('<Key>', key_handler)

# Start the image update - must be at the end
update_image()

# Keep the window open with a while loop
running = True
while True:
    window.update()

    # Exit the loop if the window is closed
    if not window.winfo_exists():
        running = False

# Ensure to clean up on exit
window.destroy()