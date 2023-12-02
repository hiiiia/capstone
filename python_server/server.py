from flask import Flask, request, jsonify
import os
import mysql.connector
import subprocess
from tensorflow import keras
from keras.applications.inception_v3 import preprocess_input
from PIL import Image
import numpy as np


global user_id_pk

host = "localhost"
user = "yong"
password = "0406"
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

app = Flask(__name__)

# 이미지를 저장할 디렉토리
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

PREDICT_FOLDER = 'predict'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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
        if not os.path.exists(app.config['UPLOAD_FOLDER']+'\\'+user_id_pk):
            os.makedirs(app.config['UPLOAD_FOLDER']+'\\'+user_id_pk)
            print("Making",user_id_pk)
        print("None Making",user_id_pk)
        filename = os.path.join(app.config['UPLOAD_FOLDER']+'\\'+user_id_pk, image.filename)
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


@app.route('/predict', methods=['POST'])
def predict_image():
    print(user_id_pk)
    if 'image' not in request.files:
        return jsonify({'error': 'No image part'})

    image = request.files['image']
    if image.filename == '':
        return jsonify({'error': 'No selected file'})

    if image:
        if not os.path.exists(app.config['PREDICT_FOLDER']+'\\'+user_id_pk):
            os.makedirs(app.config['PREDICT_FOLDER']+'\\'+user_id_pk)
            print("Making",user_id_pk)
        print("None Making",user_id_pk)
        filename = os.path.join(app.config['PREDICT_FOLDER']+'\\'+user_id_pk, image.filename)
        image.save(filename)
        loaded_model = keras.models.load_model("./ml/capstone.h5", compile=False)

        # 이미지를 불러옴
        #img_path = './ml/data/b.webp'  # 이미지 파일 경로
        img_path = filename
        # 이미지 로드
        img = Image.open(img_path)
        img = img.resize((64, 64))  # 모델이 원하는 크기로 조정
        img = np.array(img)

        # 이미지를 모델의 입력 형식에 맞게 전처리
        img = preprocess_input(img)
        img = np.expand_dims(img, axis=0)  # 배치 차원을 추가하여 (1, 64, 64, 3) 형태로 만듦

        # 모델에 이미지를 입력으로 전달하여 예측 수행
        predictions = loaded_model.predict(img)

        # 예측 결과를 해석하고 출력
        if predictions[0][0] > predictions[0][1]:
            result = "key"
        else:
            result = "wallet"

        print("Predicted class:", result)

        # 'key' 클래스에 대한 확률
        probability_key = predictions[0][0]

        # 'wallet' 클래스에 대한 확률
        probability_wallet = predictions[0][1]

        print("Probability for 'key':", probability_key)
        print("Probability for 'wallet':", probability_wallet)


        process_result = subprocess.run(["pwd", "-P"], capture_output=True, text=True)

        # 결과 출력
        print("Return Code:", process_result.returncode)
        print("Standard Output:", process_result.stdout)
        print("Standard Error:", process_result.stderr)

        position_x = "11"
        position_y = "12"
        position_z = "13"

        predcit_map_location(str(user_id_pk),position_x,position_y,position_z,result)


        return jsonify({'message': 'Image predict result : ' + result,'result' : result})
    

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_id = data.get('user_id')
    password = data.get('password')

    

    # 여기서 실제 로그인 로직을 수행합니다.
    if authenticate_user(str(user_id), str(password)):
        print("Login T")
        return jsonify({'success': True})
    
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


