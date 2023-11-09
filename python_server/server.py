# from flask import Flask, request, jsonify
# from flask_mysql_connector import MySQL

# app = Flask(__name__)

# # MySQL 데이터베이스 연결 설정
# app.config['MYSQL_DATABASE_HOST'] = 'localhost'
# app.config['MYSQL_DATABASE_USER'] = 'cap_test_user'
# app.config['MYSQL_DATABASE_PASSWORD'] = '1234'
# app.config['MYSQL_DATABASE_DB'] = 'cap_db'
# mysql = MySQL(app)

# # API 엔드포인트: 사용자 정보 조회
# @app.route('/get_users', methods=['GET'])
# def get_users():
#     conn = mysql._connect()
#     cursor = conn.cursor()

#     cursor.execute('SELECT id, username, email FROM users')
#     result = cursor.fetchall()

#     users = []
#     for user in result:
#         users.append({
#             'id': user[0],
#             'username': user[1],
#             'email': user[2]
#         })

#     conn.close()

#     return jsonify({'users': users})

# # API 엔드포인트: 사용자 추가
# @app.route('/add_user', methods=['POST'])
# def add_user():
#     data = request.get_json()
#     username = data['username']
#     email = data['email']

#     conn = mysql._connect()
#     cursor = conn.cursor()

#     cursor.execute("INSERT INTO users (username, email) VALUES (%s, %s)", (username, email))
#     conn.commit()
#     conn.close()

#     return jsonify({'message': 'User added successfully'})

# # API 엔드포인트: 데이터베이스 스키마 및 테이블 정보 조회
# @app.route('/get_schema', methods=['GET'])
# def get_schema():
#     conn = mysql._connect()
#     cursor = conn.cursor()

#     # 데이터베이스 스키마 정보 가져오기
#     cursor.execute("SHOW DATABASES")
#     databases = [database[0] for database in cursor.fetchall()]

#     # 데이터베이스 테이블 정보 가져오기
#     cursor.execute(f"USE {app.config['MYSQL_DB']}")
#     cursor.execute("SHOW TABLES")
#     tables = [table[0] for table in cursor.fetchall()]

#     # 테이블 구조 정보 가져오기
#     table_structure = {}
#     for table in tables:
#         cursor.execute(f"DESCRIBE {table}")
#         columns = cursor.fetchall()
#         table_structure[table] = [column[0] for column in columns]

#     conn.close()

#     return jsonify({'databases': databases, 'tables': tables, 'table_structure': table_structure})

# if __name__ == '__main__':
#     app.run(debug=True)
