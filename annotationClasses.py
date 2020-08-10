import cv2
import numpy as np
from PIL import Image, ImageGrab, ImageTk
import cv2


# class that holds the image and its mask
class Pic:
    def __init__(self, img):
        # the original picture scaled to 672 by 672
        self.original_picture = cv2.resize(img, (672, 672))
        # black and white version of photo
        self.BW = cv2.cvtColor(cv2.cvtColor(self.original_picture, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
        # the mask initiated to be all false
        self.mask = np.zeros((672, 672), dtype=bool)
        # the picture to show the effect of the mask on the original picture
        self.masked = np.copy(self.original_picture)
        # updates masked to match the mask
        self.update_mask(0, 0, 672, 672)
        self.state = True

    # toggles whether the output image will the masked image or the mask itself
    def toggle_state(self):
        if self.state:
            self.state = False
        else:
            self.state = True

    def get_original(self):
        return self.original_picture

    def get_BW(self):
        return self.BW

    def get_mask(self):
        return self.mask

    # gets how the cursor at its current position
    # would align with the image
    # cuts if out of bounds but retains parts of cursor that
    # are not out of bounds
    def get_alingment(self, x_pos, y_pos, cursor):
        cursor_height = np.shape(cursor)[0]
        cursor_width = np.shape(cursor)[1]
        # determines which parts of the image the cursos falls in
        x1 = int(x_pos - (cursor_height / 2))
        y1 = int(y_pos - (cursor_width / 2))
        x2 = int(x_pos + (cursor_height / 2))
        y2 = int(y_pos + (cursor_width / 2))

        # truncates the parts that are out of bounds
        x1_m = max(0, (min(671, x1)))
        y1_m = max(0, (min(671, y1)))
        x2_m = max(0, (min(671, x2)))
        y2_m = max(0, (min(671, y2)))

        # adjust cursor for truncation
        x1_c = x1_m - x1
        y1_c = y1_m - y1
        x2_c = cursor_width - abs(x2_m - x2)
        y2_c = cursor_height - abs(y2_m - y2)

        return x1_m, y1_m, x2_m, y2_m, x1_c, y1_c, x2_c, y2_c

    # outputs either the masked image or mask
    # adds in the outline of the cursor
    def get_masked_and_cursor(self, x_pos, y_pos, cursor):
        # if toggle is in the show masked image state
        if self.state:
            copy_img = np.copy(self.masked)
        # else show only the mask itself
        else:
            Temp = np.uint8(np.copy(self.mask) * 255)
            copy_img = cv2.cvtColor(Temp, cv2.COLOR_GRAY2BGR)
        # if the mouse event is out of bounds simply return the image without a cursor
        if x_pos > 671 or x_pos < 0 or y_pos > 671 or y_pos < 0:
            copy_img_rgb = cv2.cvtColor(copy_img, cv2.COLOR_BGR2RGB)
            copy_img_pil = Image.fromarray(copy_img_rgb)
            copy_img_tk = ImageTk.PhotoImage(copy_img_pil)
            return copy_img_tk

        # determine cursor alingment
        x1_m, y1_m, x2_m, y2_m, x1_c, y1_c, x2_c, y2_c = self.get_alingment(x_pos, y_pos, cursor)

        copy_cursor = cursor[y1_c:y2_c, x1_c:x2_c]
        copy_height = np.shape(copy_cursor)[0]
        copy_width = np.shape(copy_cursor)[1]

        for i in range(copy_height):
            for j in range(copy_width):
                if not copy_cursor[i, j]:
                    copy_img[i + y1_m, j + x1_m] = np.array([0, 0, 0])

        copy_img = np.uint8(copy_img)

        # convert to a tk image
        copy_img_rgb = cv2.cvtColor(copy_img, cv2.COLOR_BGR2RGB)
        copy_img_pil = Image.fromarray(copy_img_rgb)
        copy_img_tk = ImageTk.PhotoImage(copy_img_pil)

        return copy_img_tk

    # apply or remove mask from area
    def mask_area(self, x_pos, y_pos, cursor_mask, mask_unmasked):
        if x_pos > 671 or x_pos < 0 or y_pos > 671 or y_pos < 0:
            return
        # determine cursor alignment
        x1_m, y1_m, x2_m, y2_m, x1_c, y1_c, x2_c, y2_c = self.get_alingment(x_pos, y_pos, cursor_mask)

        copy_cursor = cursor_mask[y1_c:y2_c, x1_c:x2_c]
        copy_height = np.shape(copy_cursor)[0]
        copy_width = np.shape(copy_cursor)[1]

        # apply changes to mask
        for i in range(copy_height):
            for j in range(copy_width):
                if mask_unmasked:
                    self.mask[i + y1_m, j + x1_m] = copy_cursor[i, j] | self.mask[i + y1_m, j + x1_m]
                else:
                    self.mask[i + y1_m, j + x1_m] = ~(copy_cursor[i, j]) & self.mask[i + y1_m, j + x1_m]

        # update the mask
        self.update_mask(x1_m, y1_m, x2_m + 1, y2_m + 1)

    # apply changes to mask in areas specified by x1, y1, x2, y2
    def update_mask(self, x1, y1, x2, y2):
        for i in range(y1, y2):
            for j in range(x1, x2):
                if self.mask[i, j]:
                    self.masked[i, j] = self.original_picture[i, j]
                else:
                    self.masked[i, j] = self.BW[i, j]


# class that holds the cursor size and shape
class Cursor:
    def __init__(self, size_):
        self.size = size_
        self.mask = None
        self.cursor = None
        self.set_size(self.size)

    # sets the size of cursor mask and outline
    def set_size(self, s):
        thickness = 1
        w = s
        h = s
        center = (int(w / 2), int(h / 2))
        radius = min(center[0], center[1], w - center[0], h - center[1])
        Y, X = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((X - center[0]) ** 2 + (Y - center[1]) ** 2)
        self.mask = dist_from_center <= radius
        self.cursor = (dist_from_center >= (radius + thickness)) | (dist_from_center <= (radius - thickness))

    def get_cursor(self):
        return self.cursor

    def get_mask(self):
        return self.mask

    def get_size(self):
        return self.size

    # increase the size of the cursor
    def increment_size(self):
        new_size = self.size + 3
        if new_size >= 300:
            return
        self.size = new_size
        self.set_size(new_size)

    # decrease the size of the cursor
    def decrement_size(self):
        new_size = self.size - 3
        if new_size <= 5:
            return
        self.size = new_size
        self.set_size(new_size)
