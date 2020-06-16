#!/usr/bin/env python3
#############################
# Module: lasergui
# Created: Ron Grimes April 2020
# 
# Function:
'''
This is the main module for the laserpen drawing experiment.
Run this program which calls:
    * laserpen
    * laserimage
    * lasersvg
'''
#############################

from guizero import App, Box, Combo, PushButton, Text, TextBox
from tkinter import Entry, Spinbox, StringVar
import json
import os.path

from laserpen import LaserPen
from laserimage import Image

import threading

datadict = "DataDict.json"

PWR_OFF = 0
PWR_MAX = 100

# Development
# 1. Implement circle
# 2. Implement path
# 3. Implement matrix (!)
# 4. Open Setting in separate modal window.

#--------------------------------------------------------------
def build_settings(app):
    global val_ox, val_oy, val_rx, val_ry
    global se_apply, se_draw, se_toggle, se_runtime, se_quit

#---------------box = for full window
    box = Box(app, layout="auto", width="fill", height="fill", align="top") 

#--------------Start heading_box - row
    heading_box = Box(box, width="fill") 
    t = Text(heading_box, height=2, text=" Settings", font="Helvetica", size=16, align="left")

#--------------Start numbs_row - row of 3 columns
    numbs_row = Box(box, layout="grid", width="fill") 
    row_line = 0
    row_col = 0
    pad = Text(numbs_row, grid=[row_col,row_line], width=2, height=5)

#--------------Start numbs_box
    row_col += 1
    numbs_box = Box(numbs_row, layout="grid", grid=[row_col,row_line], height=30, width=130) 

    line = 0
    col = 0

    Text(numbs_box, height=2, text="pan origin:", align="left", grid=[col,line])
    val_ox = StringVar(numbs_box.tk)
    val_ox.set(str(DataDict["pantilt_origin"][0]))
    spinbox = Spinbox(numbs_box.tk, from_=-90, to=90, width=4, textvariable=val_ox, justify="right")
    col += 1
    numbs_box.add_tk_widget(spinbox, height=2, grid=[col,line], align="right")

    col += 1; pad = Text(numbs_box, grid=[col,0], width=2)

    col += 1
    Text(numbs_box, height=2, text="range:", align="left",grid=[col,line])
    val_rx = StringVar(numbs_box.tk)
    val_rx.set(str(DataDict["pantilt_range"][0]))
    spinbox = Spinbox(numbs_box.tk, from_=10, to=90, width=4, textvariable=val_rx, justify="right")
    col += 1
    numbs_box.add_tk_widget(spinbox, height=2, grid=[col,line], align="right")

    line += 1
    col = 0
    Text(numbs_box, height=2, text="tilt origin:", align="left",grid=[col,line])
    val_oy = StringVar(numbs_box.tk)
    val_oy.set(str(DataDict["pantilt_origin"][1]))
    spinbox = Spinbox(numbs_box.tk, from_=-90, to=90, width=4, textvariable=val_oy, justify="right")

    col += 1
    numbs_box.add_tk_widget(spinbox, height=2, grid=[col,line], align="right")

    col += 1; pad = Text(numbs_box, grid=[col,line], width=2)

    col += 1
    Text(numbs_box, height=2, text="range:", align="left",grid=[col,line])
    val_ry = StringVar(numbs_box.tk)
    val_ry.set(str(DataDict["pantilt_range"][1]))
    spinbox = Spinbox(numbs_box.tk, from_=10, to=90, width=4, textvariable=val_ry, justify="right")

    col += 1
    numbs_box.add_tk_widget(spinbox, height=2, grid=[col,line], align="right")
#--------------End numbs_box

    row_col += 1
    pad = Text(numbs_row, grid=[row_col,row_line], width=5)

    row_col += 1
    se_apply = PushButton(numbs_row, align="left", text="Apply", grid=[row_col,row_line],
            command=apply)

#--------------End numbs_row

#--------------Start spacer_box - row
    spacer_box = Box(box, layout="auto", height=30, width="fill")
#--------------End spacer_box

#--------------Start buttons_box
    bbox = Box(box, layout="grid", width="fill", height=120)
    line = 0
    col = -1

    col += 1; pad = Text(bbox, grid=[col,line], width=2)

#   col += 1; se_apply = PushButton(bbox, align="left", text="Apply", grid=[col,line], command=apply)
#   col += 1; pad = Text(bbox, grid=[col,line], width=2)

    col += 1; se_draw = PushButton(bbox, align="left", text="Draw box outline", grid=[col,line], command=draw_box)
    col += 1; pad = Text(bbox, grid=[col,line], width=2)

    col += 1; se_toggle = PushButton(bbox, align="left", text="Toggle laser", grid=[col,line], command=toggle_laser)
    col += 1; pad = Text(bbox, grid=[col,line], width=2)

    line += 1
    col = 0; pad = Text(bbox, grid=[col,line], height=1)

    line += 1
    col = 0
    col += 1; se_runtime = PushButton(bbox, align="left", text="Runtime", grid=[col,line], command=activate_runtime)
    col += 1; pad = Text(bbox, grid=[col,line], width=2)

    col += 1; se_quit = PushButton(bbox, align="left", text="Quit", grid=[col,line], command=lasergui_quit)
#--------------End buttons_box

    return box

#---------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------
def build_runtime(app):
    global tfile
    global rt_getfile, rt_settings, rt_drawimage, rt_quit

    # box = for full window
    wbox = Box(app, layout="auto", width="fill", height="fill") 
    
    heading_box = Box(wbox, layout="auto", width="fill") 
    t = Text(heading_box, height=2, text="Runtime", font="Helvetica", size=16, align="left")

#--------------file row
    file_box = Box(wbox, layout="auto", width="fill", height=60) 
    file_val = display_file_name("File: " + str(DataDict["default_file"]))
    tfile = Text(file_box, text=file_val, height=60, align="left")

#--------------Start spacer_box
    controls_box = Box(wbox, layout="auto", width="fill", height=5) 
    pad = Text(controls_box, width="fill")

#--------------Start buttons_box
    bbox = Box(wbox, layout="grid", width="fill", height=50)

    line = 0; col = -1
    col += 1; pad = Text(bbox, grid=[col,line], width=2)
    col += 1; rt_getfile = PushButton(bbox, text="Get file", grid=[col,line], command=load_image_fileT)
    col += 1; pad = Text(bbox, grid=[col,line], width=2)
    col += 1; rt_drawimage = PushButton(bbox, text="Draw Image", grid=[col,line], command=draw_image)
    col += 1; pad = Text(bbox, grid=[col,line], width=2)
    col += 1; rt_settings =  PushButton(bbox, text="Settings", grid=[col,line], command=activate_settings)
    col += 1; pad = Text(bbox, grid=[col,line], width=2)
    col += 1; rt_quit =  PushButton(bbox, text="Quit", grid=[col,line], command=lasergui_quit)
    rt_drawimage.disable()  # enable when we load a good file.

    return wbox

# ---------------------------------------------------------------------------------------
def activate_runtime():
    box_settings.hide()
    box_runtime.show()

def activate_settings():
    box_runtime.hide()
    box_settings.show()

# ---------------------------------------------------------------------------------------
# Button functions

def apply():
    global val_ox, val_oy, val_rx, val_ry
#   print("val_pl={}, val_pr={}, val_tl={}, val_tr={}".format(
#       val_pl.get(), val_pr.get(), val_tl.get(), val_tr.get()))
    try:
        val_ox_i = int(val_ox.get())
        val_oy_i = int(val_oy.get())
        val_rx_i = int(val_rx.get())
        val_ry_i = int(val_ry.get())
    except ValueError:
        app.warn("Warning", "Invalid number for origin, axis range. Request ignored.")
        return

#   print(DataDict["pantilt_origin"])
    origin   = (val_ox_i, val_oy_i)
    pt_range = (val_rx_i, val_ry_i)

    try:
        laserpen.set_bounds(origin, pt_range)
    except ValueError as e:
        app.warn("Warning", str(e) + " Ignored.")
    else:
        DataDict["pantilt_origin"] = origin
        DataDict["pantilt_range"]  = pt_range
        
#---------------------------------------------------------------------------
def cancel_settings_draw():
#   This vaue is picked up in laserpen & abandons the draw activity.
    laserpen.run = False

def draw_box_thr():
    se_apply.disable()
    se_draw.disable()
    se_toggle.disable()
    se_runtime.disable()
    se_quit.text = "Cancel"
    se_quit.update_command(command=cancel_settings_draw)

    image.box_100(laserpen)

    se_apply.enable()
    se_draw.enable()
    se_toggle.enable()
    se_runtime.enable()
    se_quit.text = "Quit"
    se_quit.update_command(command=lasergui_quit)

def draw_box():
    t = threading.Thread(target=draw_box_thr)
    t.start()

def draw_image_thr():
    rt_getfile.disable()
    rt_drawimage.disable()
    rt_settings.disable()
    rt_quit.text = "Cancel"
    rt_quit.update_command(command=cancel_settings_draw)

    image.draw_quickbox(app, laserpen)
    image.draw_image(app, laserpen)

    rt_getfile.enable()
    rt_drawimage.enable()
    rt_settings.enable()
    rt_quit.text = "Quit"
    rt_quit.update_command(command=lasergui_quit)

def draw_image():
    t = threading.Thread(target=draw_image_thr)
    t.start()

def toggle_laser():
    global laser_pwr
    laser_pwr = PWR_MAX if laser_pwr == PWR_OFF else PWR_OFF
    laserpen.laser_pwr(laser_pwr)

#---------------------------------------------------------------------------
def display_file_name(filename):
    max_width = 50
    if len(filename) > max_width:
#       f = filename.rsplit("/", 1)    # result = [front, back], "/" is dropped
#       filename = f[0] + "/\n" + f[1]
        filename = "\n".join(filename[i:i+max_width] for i in range(0, len(filename), max_width))
    return filename

def load_image_fileT():
    load_image_file(get_new_file=True)

def lasergui_quit():
    if app.yesno("Quit?", "Really quit?"):
        app.tk.quit()

# ---------------------------------------------------------------------------------------
# __main__ code support functions

def app_size():
    print("w = {}, h = {}".format(app.width, app.height))

def pulse():   # gets called every 100ms to allow ^C to be handled.
    pass

def load_DataDict():
    file_path = datadict
    if os.path.isfile(file_path):
        with open(datadict, "r") as read_file:
            dd = json.load(read_file)
    else:
        from datadict import DataDict as dd
    return dd

def get_file():
#   Search for file in last used directory. Current directory if directory not found.
    src_folder = "."
    try:
        dir_name = os.path.dirname(DataDict["default_file"])
        if os.path.isdir(dir_name):
            src_folder = dir_name
    except:    # recover any IO error here - all I want is a possible update on src_folder.
        pass

    myfile = app.select_file("Select file", folder=src_folder, filetypes=[["All files", "*.*"]])
    if len(myfile) == 0:
        return None
    return myfile 

def load_image_file(get_new_file=False):
    global tfile, image

    image.filename = DataDict["default_file"] 
    while True:
        if get_new_file:
            result = get_file()
            if result is None:
                return                           
            image.filename = result
        get_new_file = True

        try:
            if not os.path.isfile(image.filename):
                continue
        except:         # recover any IO error here.
            continue

        image.load_image(app)
        if image.validfile:
            break
            # and reloop
    tfile.value = display_file_name("File: " + image.filename)
    rt_drawimage.enable()  # we have a good file - enable "draw" button.
    DataDict["default_file"] = image.filename 

def save_DataDict(dd):
    with open(datadict, "w") as write_file:
        json.dump(dd, write_file, indent=2)

# ---------------------------------------------------------------------------------------
# Get vars from last run, or defaults
DataDict = load_DataDict()

laserpen = LaserPen()
laserpen.set_bounds(DataDict["pantilt_origin"], DataDict["pantilt_range"])

laser_pwr = PWR_OFF
laserpen.laser_pwr(laser_pwr)

image = Image()

app = App(title="laserpen", width=450, height=350)
app.repeat(100, pulse)       # wake up every 100ms to check for ^C & others.

#app.when_mouse_leaves = app_size     # Optionally show screen size on resize.

# Build Windows layouts
box_settings = build_settings(app)
box_runtime = build_runtime(app)
activate_runtime()

load_image_file(get_new_file=False)

try:
    app.display()

except KeyboardInterrupt:
    print()

save_DataDict(DataDict)
