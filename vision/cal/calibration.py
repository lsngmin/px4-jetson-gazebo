import cv2, glob, numpy as np

class CameraCalibration:
    # 체스보드 내부 코너 갯수 (행=7, 열=9 이면 9x6 사각형)
    pattern_size = (9, 6)

    objp = np.zeros((np.prod(pattern_size), 3), np.float32)
    objp[:, :2] = np.indices(pattern_size).T.reshape(-1, 2)

    obj_points, img_points = [], []

    for fname in glob.glob("images/*.jpg"):
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ok, corners = cv2.findChessboardCorners(gray, pattern_size)
        if ok:
            obj_points.append(objp)
            img_points.append(corners)

    h, w = gray.shape[:2]
    ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(
        obj_points, img_points, (w, h), None, None
    )

    fx, fy = K[0, 0], K[1, 1]
    cx, cy = K[0, 2], K[1, 2]

    print(f"fx={fx:.1f}, fy={fy:.1f}, cx={cx:.1f}, cy={cy:.1f}")
    print("distortion:", dist.ravel())
