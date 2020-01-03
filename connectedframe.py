#!/usr/bin/env python3

from tkinter import *
from os import putenv, getenv, system
from PIL import Image, ImageTk
from resizeimage import resizeimage
import glob
import sys
import random

#Import OMXplayer wrapper for video
from omxplayer.player import OMXPlayer
from pathlib import Path
from time import sleep
import filetype


carousel_interval = int(5) * 1000

base_path = "/home/pi/Pictures/google/photos/*/*/*"
prog_path = "/home/pi/ConnectedFrame"
carrousel_status = True
image_index = 0
image_list = []
initial_init = True

def list_images():
	images = []


	dir = base_path

	images = glob.glob(base_path, recursive=True)

	return images

def play_pause():
	global carrousel_status

	carrousel_status = not carrousel_status

	if(carrousel_status):
		img = ImageTk.PhotoImage(Image.open("/home/pi/ConnectedFrame/icons/pause.png"))
	else:
		img = ImageTk.PhotoImage(Image.open("/home/pi/ConnectedFrame/icons/play.png"))

	play_button.configure(image=img)
	play_button.image = img

def carrousel():
	if(carrousel_status):
            global image_index
            image_index = image_index + 1
            if image_index > len(image_list) - 1:
                image_index = 0
            image_path = image_list[image_index]
            image_path = random.choice(glob.glob(base_path, recursive=True))
            update_image(image_path)

	root.after(carousel_interval, carrousel)

def update_image(image_path):
        # Check for video attempt - if filetype found play the video
        kind = filetype.guess(image_path)
        if ((kind.mime == "video/mp4") or (kind.mime == "video/x-m4v") or (kind.mime == "video/quicktime")):
            # it takes about this long for omxplayer to warm up and start displaying a picture on a rpi3
            player = OMXPlayer(image_path)
            sleep(2.5)
            player.set_position(5)
            player.pause()

            sleep(2)

            player.set_aspect_mode('stretch')
            # While we fit videos into the smaller frame, videos should use the whole screen
            player.set_video_pos(0, 0, 800, 480)
            try:
                player.play()
            except Exception:
                sys.exc_clear()

            sleep(5)

            player.quit()

        else:
            img = Image.open(image_path)
            #img = resizeimage.resize_thumbnail(img, [720, 480])
            img = resizeimage.resize_contain(img, [720, 480])

            img = ImageTk.PhotoImage(img)
            center_label.configure(image=img,background='black')
            center_label.image = img

def initialize():
	global image_list, carrousel_status, initial_init
	current_carrousel_status = carrousel_status
	carrousel_status = False

	image_list = list_images()

	carrousel_status = current_carrousel_status

	if(initial_init):
		initial_init = False
		root.after(1000, initialize)
	else:
		root.after(1000, initialize)

def send_event():
        # This is where we allow to exit the GUI
        img = ImageTk.PhotoImage(Image.open("/home/pi/ConnectedFrame/icons/liked.png"))
        like_button.configure(image=img)
        like_button.image = img
        sys.exit()

root = Tk()
root.title('Connected Frame')
root.geometry('{}x{}'.format(800, 480))
root.attributes("-fullscreen", True)
root.config(cursor='none')
root.configure(background='black')
root.configure(bg="black")

initialize()

center_column = Frame(root, bg='blue', width=720, height=480)
right_column = Frame(root, bg='black', width=80, height=480)

center_column.pack_propagate(0)
right_column.pack_propagate(0)

center_column.grid(row=0, column=0, sticky="nsew")
right_column.grid(row=0, column=1, sticky="nsew")

play_icon = ImageTk.PhotoImage(Image.open("/home/pi/ConnectedFrame/icons/pause.png"))
like_icon = ImageTk.PhotoImage(Image.open("/home/pi/ConnectedFrame/icons/like.png"))

play_button = Button(right_column, image=play_icon, borderwidth=0, background="black", foreground="white", activebackgro
und="black", activeforeground="white", highlightthickness=0, command=play_pause)
like_button = Button(right_column, image=like_icon, borderwidth=0, background="black", foreground="white", activebackgro
und="black", activeforeground="white", highlightthickness=0, command=send_event)

center_image = Image.open(image_list[0])
center_photo = ImageTk.PhotoImage(center_image)
center_label = Label(center_column, image=center_photo)

center_label.pack(side="bottom", fill=BOTH, expand=1)
play_button.pack(fill=BOTH, expand=1)
like_button.pack(fill=BOTH, expand=1)

carrousel()

root.mainloop()
