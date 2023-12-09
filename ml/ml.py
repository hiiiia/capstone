from tensorflow import keras
from keras.applications.inception_v3 import preprocess_input
from PIL import Image
import numpy as np
# 저장한 모델 불러오기
loaded_model = keras.models.load_model("./ml/capstone.h5", compile=False)

# 이미지를 불러옴
img_path = './ml/data/b.webp'  # 이미지 파일 경로

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