from flask import Flask, request, jsonify
import os
import mysql.connector
import subprocess
import re
from tensorflow import keras
from keras.applications.inception_v3 import preprocess_input
from PIL import Image
import numpy as np
import cv2

global user_id_pk
original_dir = os.getcwd()

host = "localhost"
user = "root"
password = "root"
database = "capstone_s"
table_name = "users"


def insert_user(user_id, user_password):
    # MySQL 서버 정보
    try:
        # MySQL 데이터베이스에 연결
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        
        
        if connection.is_connected():
            print("MySQL 데이터베이스에 연결되었습니다.")

            # MySQL 커서 생성
            cursor = connection.cursor()


            user_pk_number = 0
            query = f"SELECT * FROM {table_name}"
            cursor.execute(query)

            # 결과 가져오기
            result = cursor.fetchall()

            # 결과 출력
            # for row in result:
            #     print(row)

            if result:
                last_row = result[-1]
                if last_row is None:
                    user_pk_number =+1 
                else:
                    user_pk_number = int(last_row[0])+1
                    
                    
            # 중복 확인을 위해 사용자 ID 검색
            query = "SELECT user_id FROM users WHERE user_id = %s"
            cursor.execute(query, (user_id,))
            existing_user = cursor.fetchone()

            if existing_user:
                print("이미 존재하는 사용자 ID입니다.")
                return False

            # 사용자 정보 삽입
            
            query = "INSERT INTO users (user_pk_number, user_id, password) VALUES (%s, %s, %s)"
            values = (user_pk_number, user_id, user_password)
            cursor.execute(query, values)
            connection.commit()
            print("사용자 정보가 성공적으로 삽입되었습니다.")
            return True

    except Exception as e:
        print(f"MySQL 연결 또는 쿼리 오류: {e}")
        return False

    finally:
        # 연결과 커서 닫기
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL 연결이 닫혔습니다.")
        
def authenticate_user(user_id, user_password):
    # MySQL 서버 정보


    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            cursor = connection.cursor()
            query = f"SELECT user_id, password FROM {table_name} WHERE user_id = %s AND password = %s"
            values = (user_id, user_password)
            cursor.execute(query, values)
            result = cursor.fetchone()

            global user_id_pk
            if result:
                user_id_pk= str(user_id)
                return True
            else:
                user_id_pk= ""
                return False

    except Exception as e:
        print(f"MySQL 연결 또는 쿼리 오류: {e}")
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()       
            
            
def map_id_insert(user_id,map_name):
    # MySQL 서버 정보
    try:
        # MySQL 데이터베이스에 연결
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            print("MySQL 데이터베이스에 연결되었습니다.")

            # MySQL 커서 생성
            cursor = connection.cursor()

            table_name = "user_maps"
            print(user_id, map_name)
            # 중복 확인을 위해 사용자 ID 검색
            query = f"SELECT user_name,map_id FROM {table_name} WHERE user_name = %s"
            values = (user_id,)
            cursor.execute(query, values)
            existing_user = cursor.fetchone()

            if existing_user:
                # 기존 Map 이름 업데이트
                #print("이미 존재하는 사용자 ID입니다.")
                _, before_map_id = existing_user
                print(f"User Name: {user_id}, Map ID: {before_map_id}")

                query = f"DROP TABLE IF EXISTS {before_map_id};"
                cursor.execute(query)
                connection.commit()

                query = f"""
                    CREATE TABLE IF NOT EXISTS {map_name} (
                        number SERIAL PRIMARY KEY,
                        x FLOAT,
                        y FLOAT,
                        z FLOAT,
                        label VARCHAR(45)
                    );
                """
                cursor.execute(query)
                connection.commit()

                query = f"UPDATE {table_name} SET map_id = %s WHERE user_name = %s;"
                values = (map_name, user_id)
                cursor.execute(query, values)
                connection.commit()
                print("사용자 정보가 성공적으로 업데이트 되었습니다.")

                return True
            
            # 사용자 정보 삽입
            else :
                #  사용자 이름, Map 이름 추가
                query = f"INSERT INTO {table_name} (user_name, map_id) VALUES (%s, %s)"
                values = (user_id, map_name)
                cursor.execute(query, values)
                connection.commit()

                query = f"""
                    CREATE TABLE IF NOT EXISTS {map_name} (
                        number SERIAL PRIMARY KEY,
                        x FLOAT,
                        y FLOAT,
                        z FLOAT,
                        label VARCHAR(45)
                    );
                """
                cursor.execute(query)
                connection.commit()
                print("Map tabel 생성")
                return True

    except Exception as e:
        print(f"MySQL 연결 또는 쿼리 오류: {e}")
        return False

    finally:
        # 연결과 커서 닫기
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL 연결이 닫혔습니다.")

            
def predcit_map_location(user_id,pos_x,pos_y,pos_z,label):
    # MySQL 서버 정보
    try:
        # MySQL 데이터베이스에 연결
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            print("MySQL 데이터베이스에 연결되었습니다.")

            # MySQL 커서 생성
            cursor = connection.cursor()

            table_name = "user_maps"
            # 중복 확인을 위해 사용자 ID 검색
            query = f"SELECT user_name,map_id FROM {table_name} WHERE user_name = %s"
            values = (user_id,)
            cursor.execute(query, values)
            existing_user = cursor.fetchone()

            if existing_user:
                _, exist_map_id = existing_user
                print(f"User Name: {user_id}, Map ID: {exist_map_id}")

                query = f"""
                    INSERT INTO {exist_map_id} (x, y, z, label)
                    VALUES (%s, %s, %s, %s);
                """
                values = (pos_x, pos_y,pos_z,label)
                cursor.execute(query, values)
                connection.commit()
                print("맵에 위치가 기록되었습니다.")

                return True
            
            # 사용자 정보 삽입
            else :
                print("Map이 존재하지 않습니다")
                return False

    except Exception as e:
        print(f"MySQL 연결 또는 쿼리 오류: {e}")
        return False

    finally:
        # 연결과 커서 닫기
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL 연결이 닫혔습니다.")


def get_map_id(user_id):
    # MySQL 서버 정보
    try:
        # MySQL 데이터베이스에 연결
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            print("MySQL 데이터베이스에 연결되었습니다.")

            # MySQL 커서 생성
            cursor = connection.cursor()

            table_name = "user_maps"
            # 중복 확인을 위해 사용자 ID 검색
            query = f"SELECT user_name,map_id FROM {table_name} WHERE user_name = %s"
            values = (user_id,)
            cursor.execute(query, values)
            existing_user = cursor.fetchone()

            if existing_user:
                # Map id find
                _, before_map_id = existing_user
                print(f"User Name: {user_id}, Map ID: {before_map_id}")


                return True, before_map_id
            
            # 사용자 정보 삽입
            else :
                return True, "No_Maps"

    except Exception as e:
        print(f"MySQL 연결 또는 쿼리 오류: {e}")
        return False

    finally:
        # 연결과 커서 닫기
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL 연결이 닫혔습니다.")


def get_map_data(user_map_id):
    # MySQL 서버 정보
    try:
        # MySQL 데이터베이스에 연결
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            print("MySQL 데이터베이스에 연결되었습니다.")

            # MySQL 커서 생성
            cursor = connection.cursor()

            # 중복 확인을 위해 사용자 ID 검색
            query = f"SELECT * FROM {user_map_id}"
            cursor.execute(query)
            result = [list(row) for row in cursor.fetchall()]

            return True, result

    except Exception as e:
        print(f"MySQL 연결 또는 쿼리 오류: {e}")
        return False, "오류"

    finally:
        # 연결과 커서 닫기
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL 연결이 닫혔습니다.")

app = Flask(__name__)

# 이미지를 저장할 디렉토리
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# 비디오 저장 디렉토리

UPLOAD_VIDEO_FOLDER = 'uploads_video'
if not os.path.exists(UPLOAD_VIDEO_FOLDER):
    os.makedirs(UPLOAD_VIDEO_FOLDER)
    
app.config['UPLOAD_VIDEO_FOLDER'] = UPLOAD_VIDEO_FOLDER


# 예측데이터 저장 디렉토리
PREDICT_FOLDER = 'predict'
if not os.path.exists(PREDICT_FOLDER):
    os.makedirs(PREDICT_FOLDER)

app.config['PREDICT_FOLDER'] = PREDICT_FOLDER


@app.route('/upload', methods=['POST'])
def upload_image():
    print(user_id_pk)
    if 'image' not in request.files:
        return jsonify({'error': 'No image part'})

    image = request.files['image']
    if image.filename == '':
        return jsonify({'error': 'No selected file'})

    if image:
        if not os.path.exists(app.config['UPLOAD_FOLDER']+'/'+user_id_pk):
            os.makedirs(app.config['UPLOAD_FOLDER']+'/'+user_id_pk)
            print("Making",user_id_pk)
        print("None Making",user_id_pk)
        filename = os.path.join(app.config['UPLOAD_FOLDER']+'/'+user_id_pk, image.filename)
        image.save(filename)

        # 명령어 실행
        result = subprocess.run(["pwd", "-P"], capture_output=True, text=True)

        # 결과 출력
        print("Return Code:", result.returncode)
        print("Standard Output:", result.stdout)
        print("Standard Error:", result.stderr)
        map_id = "test_1"
        map_id_insert(str(user_id_pk),str(map_id))

        return jsonify({'message': 'Image uploaded and saved as ' + filename})

@app.route('/upload_video', methods=['POST'])
def upload_video():
    print(user_id_pk)
    
    if 'video' not in request.files:
        return jsonify({'error': 'No video part'})

    video = request.files['video']
    video_name = ""
    if video.filename == '':
        return jsonify({'error': 'No selected file'})

    if video:
        video_name = video.filename
        if not os.path.exists(app.config['UPLOAD_VIDEO_FOLDER']+'/'+user_id_pk):
            os.makedirs(app.config['UPLOAD_VIDEO_FOLDER']+'/'+user_id_pk)
            print("Making",user_id_pk)
        print("None Making",user_id_pk)

        filename = os.path.join(app.config['UPLOAD_VIDEO_FOLDER'], user_id_pk, video.filename)
        video.save(filename)

        if not os.path.exists(app.config['UPLOAD_VIDEO_FOLDER']+'/'+user_id_pk+'/'+"frames"):
            os.makedirs(app.config['UPLOAD_VIDEO_FOLDER']+'/'+user_id_pk+'/'+"frames")
        output_dir = os.path.join(app.config['UPLOAD_VIDEO_FOLDER'], user_id_pk,"frames")

        # Add your video processing logic here, if needed
        # =====================================================
        # =====================================================
        # =====================================================
        # =====================================================
        # =====================================================
        # 비디오 파일 열기
        video = cv2.VideoCapture(filename)

        # 비디오가 열렸는지 확인
        if not video.isOpened():
            print("Error: Could not open video.")
            exit()

        target_width = 752
        target_height = 480

        # 리사이즈할 크기 설정
        resize_dim = (target_width, target_height)

        start_timestamp_ns = 10000000000  # 시작 타임스탬프 (나노초 단위)
        frame_interval_ns = 33333333    # 30 FPS에 해당하는 프레임 간격 (나노초 단위)
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
            frame_filename = os.path.join(output_dir, "{}.png".format(current_timestamp_ns))
            cv2.imwrite(frame_filename, resized_frame)  # 리사이징된 흑백 프레임 저장

            # 프레임 번호 출력
            print(count)

            count += 1

        # 비디오 파일 닫기
        video.release()

        # 타임스탬프를 별도의 파일에 저장
        timestamps_file = os.path.join(output_dir, 'timestamps.txt')
        with open(timestamps_file, 'w') as file:
            for timestamp in timestamps:
                file.write("{}\n".format(timestamp))

        print("Grayscale frames and timestamps have been saved in the folder:", timestamps_file)
        
        # =====================================================
        # =====================================================
        # =====================================================
        # =====================================================
        # =====================================================
        # =====================================================
        # =====================================================
        # =====================================================
        # =====================================================
        
        # Command execution
        system_t_path = "/home/wodbs/Dev/ORB_SLAM3/src/System_t.cc"
       # 파일이 존재하면 실행
# 파일이 존재하지 않으면 실행 
        if not os.path.isfile(system_t_path):
               subprocess.run(["mv", "/home/wodbs/Dev/ORB_SLAM3/src/System.cc", "/home/wodbs/Dev/ORB_SLAM3/src/System_t.cc"])
               subprocess.run(["mv", "/home/wodbs/Dev/ORB_SLAM3/src/System1.cc", "/home/wodbs/Dev/ORB_SLAM3/src/System.cc"])
               os.chdir("/home/wodbs/Dev/ORB_SLAM3/build")
               subprocess.run(["make"])
# 실행할 명령을 정의

        command = [
        "/home/wodbs/Dev/ORB_SLAM3/Examples/Monocular/mono_euroc",
        "/home/wodbs/Dev/ORB_SLAM3/Vocabulary/ORBvoc.txt",
        "/home/wodbs/Dev/ORB_SLAM3/Examples/Monocular/test.yaml",
        str(output_dir),
        str(output_dir + "/timestamps.txt"),
        str(video_name)
]
        os.chdir(original_dir)


        # 결과를 저장할 파일
        output_file = "out_result.txt"

        # subprocess.run을 사용하여 명령을 foreground에서 실행하고 결과를 파일로 저장합니다.
        try:
            with open(output_file, "w") as output_file_handle:
                result = subprocess.run(command, check=True, stdout=output_file_handle, stderr=subprocess.PIPE, text=True)
                print("프로세스 종료 코드:", result.returncode)
        except subprocess.CalledProcessError as e:
            print("오류 발생. 종료 코드:", e.returncode)
            print("표준 에러:\n", e.stderr)

       # output_file_handle.close()
        x_position = 0
        y_position = 0
        z_position = 0
        
        # Open the file for reading
        with open(output_file, "r") as output_file_handle:
            # Read the entire contents of the file
            file_contents = output_file_handle.read()
            #print(file_contents)


            # Use regular expressions to extract values
            match = re.search(r"Camera Position: X = (\S+), Y = (\S+), Z = (\S+)", file_contents)

            # Check if the pattern was found
            if match:
                x_value = match.group(1)
                y_value = match.group(2)
                z_value = match.group(3)

                x_position = x_value
                y_position = y_value
                z_position = z_value
                # Print or use the extracted values
                print(f"Extracted values: x = {x_value}, y = {y_value}, z = {z_value}")
            else:
                print("Pattern not found in the file.")



        # =====================================================
        # =====================================================
        # =====================================================
        # ===============================================s======
        # =====================================================
        map_id = re.sub(r'[.]','',video_name)
        map_id_insert(str(user_id_pk), str(map_id))

        return jsonify({'message': 'Video uploaded and saved as ' + filename})

@app.route('/predict', methods=['POST'])
def predict_image():
    print(user_id_pk)
    
    if 'video' not in request.files:
        return jsonify({'error': 'No video part'})

    video = request.files['video']
    video_name = ""
    if video.filename == '':
        return jsonify({'error': 'No selected file'})

    if video:
        video_name = video.filename
        if not os.path.exists(app.config['PREDICT_FOLDER']+'/'+user_id_pk):
            os.makedirs(app.config['PREDICT_FOLDER']+'/'+user_id_pk)
            print("Making",user_id_pk)
        print("None Making",user_id_pk)

        filename = os.path.join(app.config['PREDICT_FOLDER'], user_id_pk, video.filename)
        video.save(filename)

        if not os.path.exists(app.config['PREDICT_FOLDER']+'/'+user_id_pk+'/'+"frames"):
            os.makedirs(app.config['PREDICT_FOLDER']+'/'+user_id_pk+'/'+"frames")
        output_dir = os.path.join(app.config['PREDICT_FOLDER'], user_id_pk,"frames")

        # Add your video processing logic here, if needed
        # =====================================================
        # =====================================================
        # =====================================================
        # =====================================================
        # =====================================================
        # 비디오 파일 열기
        video = cv2.VideoCapture(filename)

        # 비디오가 열렸는지 확인
        if not video.isOpened():
            print("Error: Could not open video.")
            exit()

        target_width = 752
        target_height = 480

        # 리사이즈할 크기 설정
        resize_dim = (target_width, target_height)

        start_timestamp_ns = 10000000000  # 시작 타임스탬프 (나노초 단위)
        frame_interval_ns = 33333333    # 30 FPS에 해당하는 프레임 간격 (나노초 단위)
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
            frame_filename = os.path.join(output_dir, "{}.png".format(current_timestamp_ns))
            cv2.imwrite(frame_filename, resized_frame)  # 리사이징된 흑백 프레임 저장

            # 프레임 번호 출력
            print(count)

            count += 1

        # 비디오 파일 닫기
        video.release()

        # 타임스탬프를 별도의 파일에 저장
        timestamps_file = os.path.join(output_dir, 'timestamps.txt')
        with open(timestamps_file, 'w') as file:
            for timestamp in timestamps:
                file.write("{}\n".format(timestamp))

        print("Grayscale frames and timestamps have been saved in the folder:", timestamps_file)
        
        # =====================================================
        # =====================================================
        # =====================================================
        # =====================================================
        # =====================================================
        # =====================================================
        # =====================================================
        # =====================================================
        # =====================================================
        

        video = cv2.VideoCapture(filename)
        # Check if the video is opened successfully
        if not video.isOpened():
            print("Error: Could not open video.")
            exit()

        count = 0

        while True:
            # Read a frame from the video
            ret, frame = video.read()

            # If no frame is read, break out of the loop
            if not ret:
                break

            # Save the frame as it is without any modifications
            frame_filename = os.path.join(output_dir, "ml.png")
            cv2.imwrite(frame_filename, frame)
            break

        # Release the video file
        video.release()
        loaded_model = keras.models.load_model("/home/wodbs/caps/ml/capstone.h5", compile=False)

        # 이미지를 불러옴
        #img_path = './ml/data/b.webp'  # 이미지 파일 경로
        img_path = f'{output_dir}/ml.png'
        # 이미지 로드
        img = Image.open(img_path)
        img = img.resize((75, 75))  # 모델이 원하는 크기로 조정
        img = np.array(img)

        # 이미지를 모델의 입력 형식에 맞게 전처리
        img = preprocess_input(img)
        img = np.expand_dims(img, axis=0)  # 배치 차원을 추가하여 (1, 64, 64, 3) 형태로 만듦

        # 모델에 이미지를 입력으로 전달하여 예측 수행
        predictions = loaded_model.predict(img)

        class_names = ["key", "wallet", "backpack", "laptop"]  # Replace with your actual class names

        predicted_class_index = np.argmax(predictions)
        predicted_class = class_names[predicted_class_index]

        print("Predicted class:", predicted_class)

# Display probabilities for all classes
        for i, class_name in enumerate(class_names):
            print(f"Probability for '{class_name}': {predictions[0][i]}")
            



        system_t_path = "/home/wodbs/Dev/ORB_SLAM3/src/System_t.cc"
       # 파일이 존재하면 실행
# 파일이 존재하지 않으면 실행 
        if  os.path.isfile(system_t_path):
                subprocess.run(["mv", "/home/wodbs/Dev/ORB_SLAM3/src/System.cc", "/home/wodbs/Dev/ORB_SLAM3/src/System1.cc"])
                subprocess.run(["mv", "/home/wodbs/Dev/ORB_SLAM3/src/System_t.cc", "/home/wodbs/Dev/ORB_SLAM3/src/System.cc"])
                os.chdir("/home/wodbs/Dev/ORB_SLAM3/build")
                subprocess.run(["make"])
# 실행할 명령을 정의
        command = [
        "/home/wodbs/Dev/ORB_SLAM3/Examples/Monocular/mono_euroc",
        "/home/wodbs/Dev/ORB_SLAM3/Vocabulary/ORBvoc.txt",
        "/home/wodbs/Dev/ORB_SLAM3/Examples/Monocular/read.yaml",
        str(output_dir),
        str(output_dir + "/timestamps.txt"),
        str(video_name)
]



        # 결과를 저장할 파일
        output_file = "out_result.txt"
        os.chdir(original_dir)

        # subprocess.run을 사용하여 명령을 foreground에서 실행하고 결과를 파일로 저장합니다.-------------------------------------------------------------------------q
        try:
            with open(output_file, "w") as output_file_handle:
                result_process = subprocess.run(command, check=True, stdout=output_file_handle, stderr=subprocess.PIPE, text=True)
                print("프로세스 종료 코드:", result_process.returncode)
        except subprocess.CalledProcessError as e:
            print("오류 발생. 종료 코드:", e.returncode)
            print("표준 에러:\n", e.stderr)


        x_position = 0
        y_position = 0
        z_position = 0
        # Open the file for reading
        with open(output_file, "r") as output_file_handle:
            # Read the entire contents of the file
            file_contents = output_file_handle.read()
            # Use regular expressions to extract values
            match = re.search(r"Camera Position: X = (\S+), Y = (\S+), Z = (\S+)", file_contents)

            # Check if the pattern was found
            if match:
                x_value = match.group(1)
                y_value = match.group(2)
                z_value = match.group(3)

                x_position = x_value
                y_position = y_value
                z_position = z_value
                # Print or use the extracted values
                print(f"Extracted values: x = {x_value}, y = {y_value}, z = {z_value}")
            else:
                print("Pattern not found in the file.")



        # =====================================================
        # =====================================================
        # =====================================================
        # =====================================================
        # =====================================================

        predcit_map_location(str(user_id_pk),x_position,y_position,z_position,predicted_class)


        return jsonify({'message': 'Image predict result : ' + predicted_class, 'result': str(x_position)+str(y_position)+str(z_position)})
    
    
# @app.route('/predict', methods=['POST'])
# def predict_image():
#     print(user_id_pk)
#     if 'image' not in request.files:
#         return jsonify({'error': 'No image part'})

#     image = request.files['image']
#     if image.filename == '':
#         return jsonify({'error': 'No selected file'})

#     if image:
#         if not os.path.exists(app.config['PREDICT_FOLDER']+'/'+user_id_pk):
#             os.makedirs(app.config['PREDICT_FOLDER']+'/'+user_id_pk)
#             print("Making",user_id_pk)
#         print("None Making",user_id_pk)
#         filename = os.path.join(app.config['PREDICT_FOLDER']+'/'+user_id_pk, image.filename)
#         image.save(filename)
#         #loaded_model = keras.models.load_model("./ml/capstone.h5", compile=False)

#         # # 이미지를 불러옴
#         # #img_path = './ml/data/b.webp'  # 이미지 파일 경로
#         # img_path = filename
#         # # 이미지 로드
#         # img = Image.open(img_path)
#         # img = img.resize((64, 64))  # 모델이 원하는 크기로 조정
#         # img = np.array(img)

#         # # 이미지를 모델의 입력 형식에 맞게 전처리
#         # img = preprocess_input(img)
#         # img = np.expand_dims(img, axis=0)  # 배치 차원을 추가하여 (1, 64, 64, 3) 형태로 만듦

#         # # 모델에 이미지를 입력으로 전달하여 예측 수행
#         # predictions = loaded_model.predict(img)

#         # # 예측 결과를 해석하고 출력
#         # if predictions[0][0] > predictions[0][1]:
#         #     result = "key"
#         # else:
#         #     result = "wallet"

#         # print("Predicted class:", result)

#         # # 'key' 클래스에 대한 확률
#         # probability_key = predictions[0][0]

#         # # 'wallet' 클래스에 대한 확률
#         # probability_wallet = predictions[0][1]

#         # print("Probability for 'key':", probability_key)
#         # print("Probability for 'wallet':", probability_wallet)


#         process_result = subprocess.run(["pwd", "-P"], capture_output=True, text=True)

#         # 결과 출력
#         print("Return Code:", process_result.returncode)
#         print("Standard Output:", process_result.stdout)
#         print("Standard Error:", process_result.stderr)

#         position_x = "11"
#         position_y = "12"
#         position_z = "13"

#         predcit_map_location(str(user_id_pk),position_x,position_y,position_z,result)


#         return jsonify({'message': 'Image predict result : ' + result,'result' : result})
    



@app.route('/get_data_by_map_id', methods=['POST'])
def get_data_by_map_id():
    data = request.get_json()
    user_map_id = data.get('user_map')

    # 여기서 실제 로그인 로직을 수행합니다.
    flag,result_out=get_map_data(str(user_map_id))
    print(result_out)
    if(flag):
        return jsonify({'success': True,'data': result_out})
    else :
        return jsonify({'success': False, 'data': "None"})
        


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_id = data.get('user_id')
    password = data.get('password')

    

    # 여기서 실제 로그인 로직을 수행합니다.
    if authenticate_user(str(user_id), str(password)):
        flag,out_result=get_map_id(str(user_id))
        print("Login T")
        if(flag):
            return jsonify({'success': True, 'map_id':out_result })
    
    else:
        print("Login F")
        
        return jsonify({'success': False, 'error': '유저 정보가 일치하지 않습니다'})

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    user_id = data.get('user_id')
    password = data.get('password')

    if insert_user(str(user_id), str(password)):
        print("signup T")
        return jsonify({'success': True})
    
    else:
        print("signup F")
        return jsonify({'success': False, 'error': '이미 존재하는 아이디입니다'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


