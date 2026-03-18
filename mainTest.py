import os
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.resnet50 import preprocess_input

# Đường dẫn đến mô hình đã huấn luyện
project_root = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(project_root, 'Braintumor10EpochsCategorical.h5')
model = load_model(model_path)

# Hàm xử lý ảnh
def preprocess_image(image_path):
    # Kiểm tra xem file có tồn tại không
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Không thể tải ảnh tại đường dẫn: {image_path}")

    # Tải ảnh bằng OpenCV
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Không thể tải ảnh tại đường dẫn: {image_path}")

    # Chuyển đổi ảnh sang RGB + resize đúng chuẩn train
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (224, 224))
    image = np.array(image, dtype=np.float32)
    return image

# Đường dẫn đến ảnh cần dự đoán
image_path = os.path.join(project_root, 'pred', 'pred0.jpg')

try:
    # Tiền xử lý ảnh
    input_img = preprocess_image(image_path)

    # Thêm chiều kích cho ảnh
    input_img = np.expand_dims(input_img, axis=0)
    input_img = preprocess_input(input_img)

    # Dự đoán
    prediction = model.predict(input_img)

    # Xử lý dự đoán
    if prediction[0][0] > prediction[0][1]:
        print("Prediction: Normal")
    else:
        print("Prediction: Brain Tumor")

except Exception as e:
    print(f"Đã xảy ra lỗi: {e}")
