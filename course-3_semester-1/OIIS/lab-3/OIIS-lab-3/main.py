import cv2
import numpy as np


def brightness_matching(img1, img2):
    lab1 = cv2.cvtColor(img1, cv2.COLOR_BGR2LAB)
    lab2 = cv2.cvtColor(img2, cv2.COLOR_BGR2LAB)
    l1, a1, b1 = cv2.split(lab1)
    l2, a2, b2 = cv2.split(lab2)
    mean1 = np.mean(l1)
    mean2 = np.mean(l2)
    std1 = np.std(l1)
    std2 = np.std(l2)
    l1_matched = ((l1 - mean1) * (std2 / std1)) + mean2
    l1_matched = np.clip(l1_matched, 0, 255).astype(np.uint8)
    lab1_matched = cv2.merge([l1_matched, a1, b1])
    img1_matched = cv2.cvtColor(lab1_matched, cv2.COLOR_LAB2BGR)

    return img1_matched


if __name__ == "__main__":
    img1 = cv2.imread('money-2.jpg')
    img2 = cv2.imread('money-1.jpg')
    img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    img1_matched = brightness_matching(img1, img2)
    img2_matched = brightness_matching(img2, img1)

    cv2.imshow('Original1 - Original2 - Matched', img1_matched)
    cv2.imshow('Original2 - Original1 - Matched', img2_matched)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.imwrite('matched_image_2.jpg', img1_matched)
    cv2.imwrite('matched_image_1.jpg', img2_matched)