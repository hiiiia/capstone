# import mysql.connector

# user_id_pk = ""

# host = "localhost"
# user = "yong"
# password = "0406"
# database = "capstone_s"
# table_name = "users"
    
# def get_user_pk_number():

    
#     # 테이블 이름
#     table_name = "users"  # 읽어올 테이블의 이름  
          
#     try:
#         # MySQL 데이터베이스에 연결
#         connection = mysql.connector.connect(
#             host=host,
#             user=user,
#             password=password,
#             database=database
#         )

#         if connection.is_connected():
#             # MySQL 커서 생성
#             cursor = connection.cursor()

#             # 테이블에서 데이터 읽어오기
#             query = f"SELECT * FROM {table_name}"
#             cursor.execute(query)

#             # 결과 가져오기
#             result = cursor.fetchall()

#             # 결과 출력
#             # for row in result:
#             #     print(row)

#             if result:
#                 last_row = result[-1]
#                 if last_row is None:
#                     return 0
#                 else:
#                     return last_row[0]
#     except Exception as e:
#         print(f"MySQL 연결 또는 쿼리 오류: {e}")

#     finally:
#         # 연결과 커서 닫기
#         if 'connection' in locals() and connection.is_connected():
#             cursor.close()
#             connection.close()


# def insert_user(user_pk_number, user_id, user_password):
#     # MySQL 서버 정보
#     try:
#         # MySQL 데이터베이스에 연결
#         connection = mysql.connector.connect(
#             host=host,
#             user=user,
#             password=password,
#             database=database
#         )

#         if connection.is_connected():
#             print("MySQL 데이터베이스에 연결되었습니다.")

#             # MySQL 커서 생성
#             cursor = connection.cursor()

#             # 중복 확인을 위해 사용자 ID 검색
#             query = "SELECT user_id FROM users WHERE user_id = %s"
#             cursor.execute(query, (user_id,))
#             existing_user = cursor.fetchone()

#             if existing_user:
#                 print("이미 존재하는 사용자 ID입니다.")
#                 return "User already exists"

#             # 사용자 정보 삽입
#             query = "INSERT INTO users (user_pk_number, user_id, password) VALUES (%s, %s, %s)"
#             values = (user_pk_number, user_id, user_password)
#             cursor.execute(query, values)
#             connection.commit()
#             print("사용자 정보가 성공적으로 삽입되었습니다.")
#             return "User added successfully"

#     except Exception as e:
#         print(f"MySQL 연결 또는 쿼리 오류: {e}")
#         return "An error occurred"

#     finally:
#         # 연결과 커서 닫기
#         if 'connection' in locals() and connection.is_connected():
#             cursor.close()
#             connection.close()
#             print("MySQL 연결이 닫혔습니다.")
#             return "Database connection closed"
        
# def authenticate_user(user_id, user_password):
#     # MySQL 서버 정보


#     try:
#         connection = mysql.connector.connect(
#             host=host,
#             user=user,
#             password=password,
#             database=database
#         )

#         if connection.is_connected():
#             cursor = connection.cursor()
#             query = f"SELECT user_id, password FROM {table_name} WHERE user_id = %s AND password = %s"
#             values = (user_id, user_password)
#             cursor.execute(query, values)
#             result = cursor.fetchone()

#             global user_id_pk 
        
#             if result:
#                 user_id_pk= str(user_id)
#                 return True
#             else:
#                 user_id_pk= ""
#                 return False

#     except Exception as e:
#         print(f"MySQL 연결 또는 쿼리 오류: {e}")
#     finally:
#         if 'connection' in locals() and connection.is_connected():
#             cursor.close()
#             connection.close()       
            
# # 사용자 정보 삽입
# user_pk_number = int(get_user_pk_number())+1  # 사용자 고유 번호
# user_id = "new_user"  # 사용자 아이디
# user_password = "new_password"  # 사용자 패스워드

# insert_user(user_pk_number, user_id, user_password)
