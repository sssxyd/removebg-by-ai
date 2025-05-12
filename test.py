import cv2
import numpy as np
from removebg import utils
from removebg.bgmask import BackGroundMaskSeparator
from removebg import sunshine

if __name__ == "__main__":
    separator = BackGroundMaskSeparator()
    img1 = utils.read_image_to_mat("example/001-1.jpg", None)
    # img2 = utils.read_image_to_mat("example/001-2.jpg", None)
    # img3 = utils.read_image_to_mat("example/001-3.jpg", None)
    # img4 = utils.read_image_to_mat("example/001-4.jpg", None)
    imgs = [img1]
    rets = separator.calc_mask(imgs)
    mask1 = rets[0]
    sunshine_images = sunshine.sunshine(img1, mask1, True)
    for i, img in enumerate(sunshine_images):
        cv2.imwrite(f"example/sunshine-{i}.png", img)
