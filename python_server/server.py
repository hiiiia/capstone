from flask import Flask, request, jsonify
import os
import mysql.connector

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
            
            
        

app = Flask(__name__)

# 이미지를 저장할 디렉토리
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
        return jsonify({'message': 'Image uploaded and saved as ' + filename})

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


