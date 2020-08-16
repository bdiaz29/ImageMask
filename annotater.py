import cv2
import numpy as np
from PIL import Image, ImageGrab, ImageTk
import cv2
from tkinter import Frame, Label, Tk, Button, filedialog, Entry, OptionMenu, END, StringVar, Checkbutton
import tkinter as tk
from annotationClasses import Pic, Cursor
import glob
import keyboard

pics = []
index = 0
in_motion = False


# draws the masking cursors when mouse over picture
def mouse_hoover(event):
    global C, pics, index
    global pic_lbl
    new_image = pics[index].get_masked_and_cursor(event.x, event.y, C.get_cursor())
    pic_lbl.configure(image=new_image)
    pic_lbl.image = new_image


# masks area
def left_click(event):
    global C, pics, index
    global pic_lbl, in_motion
    save_backup()
    in_motion = True
    pics[index].mask_area(event.x, event.y, C.get_mask(), True)
    new_image = pics[index].get_masked_and_cursor(event.x, event.y, C.get_cursor())
    pic_lbl.configure(image=new_image)
    pic_lbl.image = new_image


# unmasks area
def right_click(event):
    global C
    global pic_lbl, pics, index, in_motion
    save_backup()
    in_motion = True
    pics[index].mask_area(event.x, event.y, C.get_mask(), False)
    new_image = pics[index].get_masked_and_cursor(event.x, event.y, C.get_cursor())
    pic_lbl.configure(image=new_image)
    pic_lbl.image = new_image


# increases the size of the cursor
def mouse_wheel(event):
    global C
    global pic_lbl, pics, index

    if keyboard.is_pressed('Ctrl'):
        if event.delta >= 0:
            zoom_in(event.x, event.y)
        else:
            zoom_out(event.x, event.y)
    else:
        if event.delta >= 0:
            C.decrement_size()
        else:
            C.increment_size()
    new_image = pics[index].get_masked_and_cursor(event.x, event.y, C.get_cursor())
    pic_lbl.configure(image=new_image)
    pic_lbl.image = new_image


# toggles the mask
def toggle_mask():
    global pics, index, pic_lbl, pics, index
    pics[index].toggle_state()
    update_img()


# saves backup of mask when click is started
def save_backup():
    global pics, index, in_motion
    if not in_motion:
        pics[index].set_backup()


def revert():
    global pics, index
    pics[index].revert_to_previous()
    update_img()


def move_forward(event):
    global index, pics, pic_lbl, OptionList, tkvar
    length = len(pics)
    inc = index + 1
    if inc >= length:
        return
    index = inc
    mask_type = OptionList[pics[index].get_mask_type()]
    tkvar.set(mask_type)

    update_img()


def move_backward(event):
    global index, pics, pic_lbl, C, tkvar
    dec = index - 1
    if dec < 0:
        return
    index = dec
    mask_type = OptionList[pics[index].get_mask_type()]
    tkvar.set(mask_type)
    update_img()


def change_mask_type(event):
    global OptionDict, index, pics
    color_index = OptionDict[event]
    # set a new color scale
    pics[index].set_mask_type(color_index)
    # update image
    update_img()


def motion_stopped(event):
    global in_motion
    in_motion = False


def zoom_in(x, y):
    global pics
    global index
    pics[index].zoom_in(x, y)
    update_img()


def zoom_out(x, y):
    global pics
    global index
    pics[index].zoom_out(x, y)
    update_img()


def mid(event):
    global in_motion, index, pics
    p=0
    test=in_motion
    if not in_motion:
        pics[index].set_old(event.x, event.y)
        in_motion = True

def pan(event):
    global pics
    global index
    global in_motion, index, pics
    p = 0
    test = in_motion
    if not in_motion:
        pics[index].set_old(event.x, event.y)
        in_motion = True

    pics[index].pan(event.x, event.y)
    update_img()


def update_img():
    global C
    global pics
    global index
    init = pics[index].get_masked_and_cursor(-1, -1, C.get_cursor())
    pic_lbl.configure(image=init)
    pic_lbl.image = init


def save_files():
    global pics, sizetxt_1, sizetxt_2, c1, var
    files = [('npz Files', '*.npz')]
    path = filedialog.asksaveasfile(initialdir="C:/numy/", filetypes=files, defaultextension=files)

    option = var.get()

    if path == '':
        return
    image = []
    mask = []
    for pic in pics:
        if option == 0:
            height = int(sizetxt_1.get())
            width = int(sizetxt_2.get())
        elif option == 1:
            height, width = pic.get_dim()
        else:
            print("problem with var")
            return

        # resize and validate
        img = pic.get_original()
        mk = np.uint8(pic.get_mask() * 255)
        # resize to specified values
        img = cv2.resize(img, (width, height))
        mk = cv2.resize(mk, (width, height))
        msk = np.zeros((height, width), dtype=bool)
        # validate mask value
        for i in range(height):
            for j in range(width):
                if mk[i, j] > 0:
                    msk[i, j] = True

        image += [img]
        mask += [msk]

    mask = np.array(mask)
    image = np.array(image)
    np.savez(path.name, image=image, mask=mask)

def load_images():
    global pic_lbl, C, index, window
    global save, mask_toggle, pics
    path = filedialog.askdirectory()
    if path == '' or path is None:
        return

    file_list = glob.glob(path + "/*.jpg")
    file_list.extend(glob.glob(path + "/*.png"))
    file_list.extend(glob.glob(path + "/*.jpeg"))
    for file in file_list:
        # attempt to load image
        try:
            img = cv2.imread(file)
            pics += [Pic(img)]
        except:
            print("error loading image ")

    save.configure(state='normal')
    mask_toggle.configure(state='normal')
    revert_btn.configure(state='normal')
    color_map.configure(state='normal')

    init = pics[index].get_masked_and_cursor(-1, -1, C.get_cursor())
    pic_lbl.configure(image=init)
    pic_lbl.image = init

    pic_lbl.bind("<Motion>", mouse_hoover)
    pic_lbl.bind("<B1-Motion>", left_click)
    pic_lbl.bind("<ButtonPress-1>", left_click)
    pic_lbl.bind("<B3-Motion>", right_click)
    pic_lbl.bind("<ButtonPress-3>", right_click)
    pic_lbl.bind("<MouseWheel>", mouse_wheel)

    pic_lbl.bind("Button-2", mid)
    pic_lbl.bind("<B2-Motion>", pan)

    pic_lbl.bind("<ButtonRelease-2>", motion_stopped)
    pic_lbl.bind("<ButtonRelease-1>", motion_stopped)
    pic_lbl.bind("<ButtonRelease-3>", motion_stopped)

    window.bind("<Right>", move_forward)
    window.bind("<Left>", move_backward)


window = Tk()
window.title("Bruno'd Image Annotation Program")
window.geometry('750x850')

# im = Pic(img)
im = None
C = Cursor(25)

command_frame = Frame(master=window)
command_frame.grid(column=0, row=0, padx=5, pady=5)

load_pic = Button(master=command_frame, text="load image", command=load_images)
load_pic.grid(column=0, row=0, padx=5, pady=5, sticky="W")

mask_toggle = Button(master=command_frame, text="toggle mask", command=toggle_mask, state='disabled')
mask_toggle.grid(column=1, row=0, padx=5, pady=5, sticky="W")

save = Button(master=command_frame, text="save mask", state='disabled', command=save_files)
save.grid(column=0, row=1, padx=5, pady=5, sticky="W")

var = tk.IntVar()
var.set(0)
c1 = Checkbutton(command_frame, text='save in original dimension', variable=var, onvalue=1, offvalue=0)
c1.grid(column=0, row=2, padx=5, pady=5, sticky="W")

targer_lbl = Label(master=command_frame, text='target size')
targer_lbl.grid(column=1, row=1, padx=5, pady=5, sticky="W")

sizetxt_1 = Entry(master=command_frame, width=10)
sizetxt_1.grid(column=2, row=1, padx=5, pady=5, sticky="W")
sizetxt_1.insert(END, '224')

sizetxt_2 = Entry(master=command_frame, width=10)
sizetxt_2.grid(column=3, row=1, padx=5, pady=5, sticky="W")
sizetxt_2.insert(END, '224')

revert_btn = Button(master=command_frame, text="revert change", state='disabled', command=revert)
revert_btn.grid(column=2, row=0, padx=5, pady=5, sticky="W")

OptionList = [
    "AUTUMN",
    "BONE",
    "JET",
    "WINTER",
    "RAINBOW",
    "OCEAN",
    "SUMMER",
    "SPRING",
    "COOL",
    "HSV",
    "PINK",
    "HOT",
    "PARULA",
    "MAGMA",
    "INFERNO",
    "PLASMA",
    "VIRIDIS",
    "CIVIDIS",
    "TWILIGHT",
    "TWILIGHT_SHIFTED",
    "TURBO",
    "GRAYSCALE"
]

OptionDict = {
    "AUTUMN": 0,
    "BONE": 1,
    "JET": 2,
    "WINTER": 3,
    "RAINBOW": 4,
    "OCEAN": 5,
    "SUMMER": 6,
    "SPRING": 7,
    "COOL": 8,
    "HSV": 9,
    "PINK": 10,
    "HOT": 11,
    "PARULA": 12,
    "MAGMA": 13,
    "INFERNO": 14,
    "PLASMA": 15,
    "VIRIDIS": 16,
    "CIVIDIS": 17,
    "TWILIGHT": 18,
    "TWILIGHT_SHIFTED": 19,
    "TURBO": 20,
    "GRAYSCALE": 21
}

tkvar = StringVar(window)
tkvar.set('GRAYSCALE')  # set the default option
color_map = OptionMenu(command_frame, tkvar, *OptionList, command=change_mask_type)
color_map.config(width=15, state='disabled')
color_map.grid(column=3, row=0, padx=5, pady=5, sticky="W")

copy_img_pil = Image.fromarray(np.uint8(np.zeros((672, 672, 3))))
init = ImageTk.PhotoImage(copy_img_pil)
pic_frame = Frame(master=window, height=700, width=700)
pic_frame.grid(column=0, row=1, padx=5, pady=5)
pic_lbl = Label(master=pic_frame, image=init, cursor='plus')
pic_lbl.grid(column=0, row=0, padx=5, pady=5)
pic_lbl.image = init

window.mainloop()
