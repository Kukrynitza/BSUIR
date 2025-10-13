import cv2
import numpy as np

def gaussian(img):
    gaussian_image  = cv2.GaussianBlur(img,(7,7),0)
    cv2.imshow('MyPhoto', gaussian_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def cutting(img):
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    im = cv2.filter2D(img, -1, kernel)
    cv2.imshow('MyPhoto', im)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def median(img):
    median_image = cv2.medianBlur(img, 7)
    cv2.imshow('MyPhoto', median_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def sobel(img):
    kernel = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    im = cv2.filter2D(img, -1, kernel)
    cv2.imshow('MyPhoto', im)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def laplas(img):
    kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])
    im = cv2.filter2D(img, -1, kernel)
    cv2.imshow('MyPhoto', im)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    img = cv2.imread('Elk.jpg')
    cv2.imshow('Elk', img)
    cv2.waitKey(0)
    gaussian(img)
    median(img)
    cutting(img)
    sobel(img)
    laplas(img)