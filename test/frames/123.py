import numpy as np
import cv2
import glob


checkerboard_size = (6, 8)
square_size = 3.0 


objp = np.zeros((checkerboard_size[0] * checkerboard_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:checkerboard_size[0], 0:checkerboard_size[1]].T.reshape(-1, 2)
objp = objp * square_size


objpoints = [] 
imgpoints = [] 

images = glob.glob('/home/wodbs/test/frames/*.png')

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


    ret, corners = cv2.findChessboardCorners(gray, checkerboard_size, None)


    if ret == True:
        objpoints.append(objp)
        imgpoints.append(corners)


        cv2.drawChessboardCorners(img, checkerboard_size, corners, ret)
        cv2.imshow('img', img)
        cv2.waitKey(500)

cv2.destroyAllWindows()


ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

np.savez('/home/wodbs/test/frames/calibration_result.npz', mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs)


calibration_result = np.load('/home/wodbs/test/frames/calibration_result.npz')
print("Camera matrix:\n", calibration_result['mtx'])
print("Distortion coefficients:\n", calibration_result['dist'])


