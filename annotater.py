import cv2
import numpy as np
from PIL import Image, ImageGrab, ImageTk
import cv2
from tkinter import Frame, Label, Tk, Button, filedialog
from annotationClasses import Pic, Cursor


# draws the masking cursors when mouse over picture
def mouse_hoover(event):
    global im
    global C
    global pic_lbl
    new_image = im.get_masked_and_cursor(event.x, event.y, C.get_cursor())
    pic_lbl.configure(image=new_image)
    pic_lbl.image = new_image


# masks area
def left_click(event):
    global im
    global C
    global pic_lbl
    im.mask_area(event.x, event.y, C.get_mask(), True)
    new_image = im.get_masked_and_cursor(event.x, event.y, C.get_cursor())
    pic_lbl.configure(image=new_image)
    pic_lbl.image = new_image


# unmasks area
def right_click(event):
    global im
    global C
    global pic_lbl
    # def mask_area(self, x_pos, y_pos, cursor_mask, mask_unmasked):
    im.mask_area(event.x, event.y, C.get_mask(), False)
    new_image = im.get_masked_and_cursor(event.x, event.y, C.get_cursor())
    pic_lbl.configure(image=new_image)
    pic_lbl.image = new_image


# increases the size of the cursor
def mouse_wheel(event):
    global im
    global C
    global pic_lbl
    if event.delta >= 0:
        C.decrement_size()
    else:
        C.increment_size()
    new_image = im.get_masked_and_cursor(event.x, event.y, C.get_cursor())
    pic_lbl.configure(image=new_image)
    pic_lbl.image = new_image


# toggles the mask
def toggle_mask():
    global im, pic_lbl
    im.toggle_state()
    init = im.get_masked_and_cursor(-1, -1, C.get_cursor())
    pic_lbl.configure(image=init)
    pic_lbl.image = init


def load_image():
    global pic_lbl, im, C
    global save, mask_toggle
    path = filedialog.askopenfilename(initialdir="E:/machine learning/example/", title="Select file",
                                      filetypes=(
                                          ("all files", "*.*"), ("jpg files", "*.jpg"), ("png files", "*.png")))
    if path == '':
        return

    # attempt to load image
    try:
        img = cv2.imread(path)
        im = Pic(img)
    except:
        print("error loading image ")

    save.configure(state='normal')
    mask_toggle.configure(state='normal')

    init = im.get_masked_and_cursor(-1, -1, C.get_cursor())
    pic_lbl.configure(image=init)
    pic_lbl.image = init

    pic_lbl.bind("<Motion>", mouse_hoover)
    pic_lbl.bind("<B1-Motion>", left_click)
    pic_lbl.bind("<Button-1>", left_click)
    pic_lbl.bind("<B3-Motion>", right_click)
    pic_lbl.bind("<Button-3>", right_click)
    pic_lbl.bind("<MouseWheel>", mouse_wheel)


def save_files():
    global im
    files = [('npz Files', '*.npz')]
    path = filedialog.asksaveasfile(initialdir="C:/numy", filetypes=files, defaultextension=files)
    if path == '' or path is None:
        return
    image = np.array([im.get_original()])
    mask = np.array([im.get_mask()])
    np.savez(path.name, image=image, mask=mask)


window = Tk()
window.title("Bruno's Image Annotation Program")
window.geometry('750x750')

# im = Pic(img)
im = None
C = Cursor(25)

command_frame = Frame(master=window)
command_frame.grid(column=0, row=0, padx=5, pady=5)

load_pic = Button(master=command_frame, text="load image", command=load_image)
load_pic.grid(column=0, row=0, padx=5, pady=5, sticky="W")

mask_toggle = Button(master=command_frame, text="toggle mask", command=toggle_mask, state='disabled')
mask_toggle.grid(column=1, row=0, padx=5, pady=5, sticky="W")

save = Button(master=command_frame, text="save mask", state='disabled', command=save_files)
save.grid(column=2, row=0, padx=5, pady=5, sticky="W")

copy_img_pil = Image.fromarray(np.uint8(np.zeros((672, 672, 3))))
init = ImageTk.PhotoImage(copy_img_pil)
pic_frame = Frame(master=window, height=700, width=700)
pic_frame.grid(column=0, row=1, padx=5, pady=5)
pic_lbl = Label(master=pic_frame, image=init)
pic_lbl.grid(column=0, row=0, padx=5, pady=5)
pic_lbl.image = init

window.mainloop()
