import cv2 as cv # type: ignore
import os
import numpy as np # type: ignore

def rescale(frame, scale=1):
  w = int(frame.shape[1] * scale)
  h = int(frame.shape[0] * scale)
  if scale < 1:
    return cv.resize(frame, (w, h), interpolation=cv.INTER_AREA)
  return cv.resize(frame, (w, h), interpolation=cv.INTER_CUBIC)

def rescale512(img, h=512, w=512, locked=True):
  if locked:
    scale = min(w/img.shape[1], h/img.shape[0])
    return rescale(img, scale=scale)
  return cv.resize(img, (w, h), interpolation=cv.INTER_AREA)

def recolor(img, r, g, b):
  imgarr = np.array(img)
  imgarr[:] = r,g,b
  return imgarr

def get_edges1(img, blur_kernel=-1):
  if blur_kernel != -1:
    img = cv.GaussianBlur(img, (blur_kernel, blur_kernel), cv.BORDER_DEFAULT)
  edge_img = cv.Canny(img, 125, 175)
  return edge_img

def get_edges2(img, blur_kernel=-1):
  if blur_kernel != -1:
    img = cv.blur(img, (blur_kernel, blur_kernel), cv.BORDER_DEFAULT)
  edge_img = cv.Canny(img, 125, 175)
  return edge_img

def get_edges3(img, blur_kernel=-1):
  if blur_kernel != -1:
    img = cv.medianBlur(img, blur_kernel, cv.BORDER_DEFAULT)
  edge_img = cv.Canny(img, 125, 175)
  return edge_img

def get_edges4(img, blur_diameter=-1):
  if blur_diameter != -1:
    img = cv.bilateralFilter(img, blur_diameter, 15, 15, cv.BORDER_DEFAULT)
  edge_img = cv.Canny(img, 125, 175)
  return edge_img

def crop(img, x1=0, y1=0, x2=-1, y2=-1):
  if x2 == -1:
    x2 = img.shape[1]
    y2 = img.shape[0]
  return img[x1:x2, y1:y2]

# CCW if angle > 0
# CW if angle < 0
def rotate(img, angle, AoR=None):
  h = img.shape[0]
  w = img.shape[1]

  if AoR is None:
    AoR = (w//2, h//2)

  rotMtx = cv.getRotationMatrix2D(AoR, angle, 1.0)

  return cv.warpAffine(img, rotMtx, (w, h))

def convert_to_gray(img):
  return cv.cvtColor(img, cv.COLOR_BGR2GRAY)

def convert_to_rgb(img):
  return cv.cvtColor(img, cv.COLOR_BGR2RGB)

if __name__ == "__main__":
  dir = "blueprints/"
  imgs = os.listdir(dir)
  for i in imgs:
    img = cv.imread(os.path.join(dir, i))
    cv.imshow("Warship Blueprint", img)
    # cv.imshow("Resized Warship Blueprint", rescale(img))
    # cv.imshow("512x512 Resized Warship Blueprint", rescale512(img))
    # cv.imshow("Recolored Warship Blueprint", recolor(img, 0, 0, 255))
    # cv.imshow("Grayscale Image", convert_to_gray(img))
    # cv.imshow("RGB Image", convert_to_rgb(img))
    # cv.imshow("Gaussian", get_edges1(img, blur_kernel=3))
    # cv.imshow("Normal", get_edges2(img, blur_kernel=3))
    cv.imshow("Median", get_edges3(img, blur_kernel=3))
    cv.imshow("Bilateral", get_edges4(img, blur_diameter=3))
    # cv.imshow("Cropped", crop(rescale512(img), x2 = 250, y2 = 250))
    # cv.imshow("Rotated", rotate(rescale512(img), 45))

    cv.waitKey()
    