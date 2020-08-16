import cv2
import numpy as np
from PIL import Image, ImageGrab, ImageTk
import cv2


# class that holds the image and its mask
class Pic:
    def __init__(self, img):
        # save the height and width of the original picture
        height = np.shape(img)[0]
        width = np.shape(img)[1]
        self.original_height = height
        self.original_width = width
        # the original picture scaled to 672 by 672
        self.original_picture = cv2.resize(img, (672, 672))
        # black and white version of photo
        self.BW = cv2.cvtColor(cv2.cvtColor(self.original_picture, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
        # the mask initiated to be all false
        self.mask = np.zeros((672, 672), dtype=bool)
        # the picture to show the effect of the mask on the original picture
        # self.masked = np.copy(self.original_picture)
        self.masked = np.copy(self.BW)
        # updates masked to match the mask
        # self.update_mask(0, 0, 672, 672)

        self.state = True
        self.backup = []
        self.color_state = 21
        self.x1 = 0
        self.y1 = 0
        self.x2 = 671
        self.y2 = 671
        self.scale = (self.x2 - self.x1) / 671
        self.sizes = [671, 604, 537, 470, 403, 336, 268, 201, 134, 67]
        self.size_index = 0

        self.x1_old = 0
        self.y1_old = 0
        self.x2_old = 671
        self.y2_old = 671

        self.x_old = 0
        self.y_old = 0

    def set_old(self, x, y):
        self.x1_old = self.x1
        self.y1_old = self.y1
        self.x2_old = self.x2
        self.y2_old = self.y2

        self.x_old = x
        self.y_old = y
        p=0

    # zooms in
    def zoom_in(self, x, y):
        # zoom limit
        if self.size_index + 1 >= len(self.sizes):
            return
        self.size_index += 1
        size = self.sizes[self.size_index]
        # convert the read in x and y value into the actual values
        # scale x_pos
        x_pos = int((x * self.scale) + self.x1)
        y_pos = int((y * self.scale) + self.y1)

        # determine new center
        # detemine the offset for the center
        x_off = int(((x / 671) - .5) * size)
        y_off = int(((y / 671) - .5) * size)

        x_center = x_pos - x_off
        y_center = y_pos - y_off

        # set new window values
        self.x1, self.y1, self.x2, self.y2 = self.center_on(size, x_center, y_center)
        # set new scale
        self.scale = (self.x2 - self.x1) / 671

    # zooms in
    def zoom_out(self, x, y):
        # zoom limit
        if self.size_index - 1 < 0:
            return
        self.size_index -= 1
        size = self.sizes[self.size_index]
        # convert the read in x and y value into the actual values
        # scale x_pos
        x_pos = int((x * self.scale) + self.x1)
        y_pos = int((y * self.scale) + self.y1)

        # determine new center
        # detemine the offset for the center
        x_off = int(((x / 671) - .5) * size)
        y_off = int(((y / 671) - .5) * size)

        x_center = x_pos - x_off
        y_center = y_pos - y_off

        # set new window values
        self.x1, self.y1, self.x2, self.y2 = self.center_on(size, x_center, y_center)
        # set new scale
        self.scale = (self.x2 - self.x1) / 671

    # pans around the zoomed image
    def pan(self, x, y, ):
        size = self.sizes[self.size_index]

        x_off_old_0 = int(((self.x_old / 671) - .5) * size)
        y_off_old_0 = int(((self.y_old / 671) - .5) * size)

        x_off_old = int((self.x_old / 671) * size)
        y_off_old = int((self.y_old / 671) * size)

        x_off_new = int((x / 671) * size)
        y_off_new = int((y / 671) * size)

        x_diff = x_off_old - x_off_new
        y_diff = y_off_old - y_off_new

        x_pos_old_center = int((self.x_old * self.scale) + self.x1_old)-x_off_old_0
        y_pos_old_center = int((self.y_old * self.scale) + self.y1_old)-y_off_old_0

        x_center = x_pos_old_center + x_diff
        y_center = y_pos_old_center + y_diff

        self.x1, self.y1, self.x2, self.y2 = self.center_on(size, x_center, y_center)

    # centers the window on
    def center_on(self, size, x, y):
        mid = int(size / 2)
        # probable new x1 and y1 values  before
        # accouting for bounds
        prob_x = x - mid
        prob_y = y - mid

        # determine the offset to determne new window values
        x_sub = min((x - mid), 0)
        y_sub = min((y - mid), 0)
        x_add = min((671 - (x + mid)), 0)
        y_add = min((671 - (y + mid)), 0)

        x_offset = prob_x - x_sub + x_add
        y_offset = prob_y - y_sub + y_add

        # calculate new window values
        xmin = x_offset
        ymin = y_offset
        xmax = x_offset + size
        ymax = y_offset + size

        return xmin, ymin, xmax, ymax

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
        # resize to show zoom window
        copy_img = copy_img[self.y1:self.y2, self.x1:self.x2]
        copy_img = cv2.resize(copy_img, (672, 672), interpolation=cv2.INTER_NEAREST)

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
    def mask_area(self, x, y, cursor, mask_unmasked):
        if x > 671 or x < 0 or y > 671 or y < 0:
            return
        # determine cursor alignment
        # rescale cursor
        c_height = int(np.shape(cursor)[0] * self.scale)
        c_width = int(np.shape(cursor)[1] * self.scale)
        cursor_mask = cv2.resize(np.uint8(cursor * 255), (c_width, c_height), interpolation=cv2.INTER_NEAREST)
        cursor_mask = np.array((cursor_mask / 255), dtype=bool)

        # scale x_pos
        x_pos = int((x * self.scale) + self.x1)
        y_pos = int((y * self.scale) + self.y1)

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

    # change the mask type
    def set_mask_type(self, type_num):
        # change the BW foreground
        if type_num > 20:
            self.BW = cv2.cvtColor(cv2.cvtColor(self.original_picture, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
            self.color_state = 21
        else:
            self.BW = cv2.applyColorMap(self.original_picture, type_num)
            self.color_state = type_num
        # updates masked to match the mask
        self.update_mask(0, 0, 672, 672)

    def get_mask_type(self):
        return self.color_state

    # create back up copies of mask  up to ten versions
    def set_backup(self):
        # if number of backups exceeds 10 pop the oldest and insert
        if len(self.backup) > 10:
            self.backup.pop(0)
            self.backup += [np.copy(self.mask)]
        else:
            self.backup += [np.copy(self.mask)]

    # reverts current mask to previous back up
    def revert_to_previous(self):
        # if there are no backups simply return
        if len(self.backup) <= 0:
            return
        else:
            # pop the top of the backup stack
            self.mask = self.backup.pop()
            # update masked to reflect reversion
            self.update_mask(0, 0, 672, 672)

    def get_dim(self):
        return self.original_height, self.original_width


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
