import cv2
import numpy as np

points = []


def mouse_callback(event, x, y, flags, param):
    global points
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))


def interactive_region_segmentation(img):
    global points
    points = []

    cv2.imshow('Выберите 3 и больше точки и нажмите ENTER', img)
    cv2.setMouseCallback('Выберите 3 и больше точки и нажмите ENTER', mouse_callback)
    cv2.waitKey(0)

    if len(points) > 2:
        mask = np.zeros(img.shape[:2], np.uint8)
        pts_array = np.array(points, np.int32)
        cv2.fillPoly(mask, [pts_array], 255)
        segmented = cv2.bitwise_and(img, img, mask=mask)
        return segmented
    return img


def canny_segmentation(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask = np.zeros_like(gray)
    cv2.drawContours(mask, contours, -1, 255, -1)
    segmented = cv2.bitwise_and(img, img, mask=mask)
    return segmented


if __name__ == '__main__':
    img = cv2.imread("Elk-2.jpg")
    result_canny = canny_segmentation(img)
    cv2.imshow('canny_segmentation', result_canny)
    cv2.waitKey(0)

    result_region = interactive_region_segmentation(img)
    cv2.imshow('interactive_region_segmentation', result_region)
    cv2.waitKey(0)
    cv2.destroyAllWindows()