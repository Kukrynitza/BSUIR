import cv2
import numpy as np


def create_anaglyph(left_img, right_img):
    right_img = cv2.resize(right_img, (left_img.shape[1], left_img.shape[0]))

    b_left, g_left, r_left = cv2.split(left_img)
    b_right, g_right, r_right = cv2.split(right_img)

    anaglyph = cv2.merge([b_right, g_right, r_left])

    return anaglyph


if __name__ == '__main__':
    left = cv2.imread('money.jpg')
    right = cv2.imread('money-2.jpg')

    stereo = create_anaglyph(left, right)
    cv2.imshow('Stereoscopic Anaglyph', stereo)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
