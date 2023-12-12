# -*- coding: utf-8 -*-

import cv2
import os

# 저장할 폴더 이름
folder_name = 'frames'

# 폴더가 없으면 생성
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# 비디오 파일 열기
video = cv2.VideoCapture('video.mp4')

# 비디오가 열렸는지 확인
if not video.isOpened():
    print("Error: Could not open video.")
    exit()

target_width = 752
target_height = 480

# 리사이즈할 크기 설정
resize_dim = (target_width, target_height)

start_timestamp_ns = 10000000000  # 시작 타임스탬프 (나노초 단위)
frame_interval_ns = 33333333.33     # 30 FPS에 해당하는 프레임 간격 (나노초 단위)
count = 0
timestamps = []  # 타임스탬프를 저장할 리스트

while True:
    # 비디오에서 프레임 읽기
    ret, frame = video.read()

    # 프레임이 없으면 종료
    if not ret:
        break

    # 흑백으로 변환
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # 이미지 리사이징
    resized_frame = cv2.resize(gray_frame, resize_dim, interpolation = cv2.INTER_AREA)

    # 현재 프레임의 타임스탬프 계산
    current_timestamp_ns = start_timestamp_ns + (count * frame_interval_ns)
    timestamps.append(current_timestamp_ns)

    # 타임스탬프를 파일 이름으로 사용하여 프레임 저장
    frame_filename = os.path.join(folder_name, "{}.png".format(current_timestamp_ns))
    cv2.imwrite(frame_filename, resized_frame)  # 리사이징된 흑백 프레임 저장

    # 프레임 번호 출력
    print(count)

    count += 1

# 비디오 파일 닫기
video.release()

# 타임스탬프를 별도의 파일에 저장
timestamps_file = os.path.join(folder_name, 'timestamps.txt')
with open(timestamps_file, 'w') as file:
    for timestamp in timestamps:
        file.write("{}\n".format(timestamp))

print("Grayscale frames and timestamps have been saved in the folder:", folder_name)

