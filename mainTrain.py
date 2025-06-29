import os
import cv2
from PIL import Image
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split
from tensorflow.keras.applications import ResNet50
import tensorflow as tf


print(f"TensorFlow version: {tf.__version__}")

INPUT_SIZE = 224    
BATCH_SIZE = 32
EPOCHS = 20  # Tăng số lượng epoch để mô hình có thể học lâu hơn
LEARNING_RATE = 0.0001  # Tốc độ học

# Đọc dữ liệu
image_directory = 'D:/BRT350/brain_tumor/datasets/'
no_tumor_images = os.listdir(image_directory + 'no/')
yes_tumor_images = os.listdir(image_directory + 'yes/')

dataset = []
labels = []

for image_name in no_tumor_images:
    if image_name.endswith('.jpg'):
        image_path = os.path.join(image_directory + 'no/', image_name)
        image = cv2.imread(image_path)
        if image is not None:
            image = Image.fromarray(image, 'RGB')
            image = image.resize((INPUT_SIZE, INPUT_SIZE))
            dataset.append(np.array(image))
            labels.append(0)

for image_name in yes_tumor_images:
    if image_name.endswith('.jpg'):
        image_path = os.path.join(image_directory + 'yes/', image_name)
        image = cv2.imread(image_path)
        if image is not None:
            image = Image.fromarray(image, 'RGB')
            image = image.resize((INPUT_SIZE, INPUT_SIZE))
            dataset.append(np.array(image))
            labels.append(1)

dataset = np.array(dataset)
labels = np.array(labels)

# Split dữ liệu thành train và test
x_train, x_test, y_train, y_test = train_test_split(dataset, labels, test_size=0.2, random_state=42)

# Chuyển đổi nhãn thành one-hot encoding chuyển từ số đưa vào chuyển thành vector để cho modal dễ đọc hơn
y_train = tf.keras.utils.to_categorical(y_train, num_classes=2)
y_test = tf.keras.utils.to_categorical(y_test, num_classes=2)

# Tạo Data Augmentation
datagen = ImageDataGenerator(
    rotation_range=30,# Xoay ảnh tối đa 30 độ.
    width_shift_range=0.3,# Dịch ảnh ngang tối đa 30% kích thước ảnh.
    height_shift_range=0.3, # 
    shear_range=0.3,
    zoom_range=0.3,
    horizontal_flip=True,
    fill_mode='nearest'
)

# Sử dụng mô hình ResNet50 pre-trained
base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(INPUT_SIZE, INPUT_SIZE, 3))
# thư viện lưu data ảnh

# Đóng băng các lớp của mô hình base
for layer in base_model.layers:
    layer.trainable = False

# Tạo mô hình mới với các lớp tùy chỉnh
model = Sequential([
    base_model,
    Flatten(),# khi mà rgb nó là 3 màu thì nó sẽ đưa về vector mày nhìn theo biến đổi vector
    Dense(512, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.01)),# 1 lớp có 512 ne ron n
    Dropout(0.5),
    Dense(2, activation='softmax')
])

# Biên dịch mô hình
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE),
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# Cơ chế Early Stopping
early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=4, restore_best_weights=True)

# Huấn luyện mô hình và lưu lịch sử
history = model.fit(datagen.flow(x_train, y_train, batch_size=BATCH_SIZE),
                    epochs=EPOCHS,
                    validation_data=(x_test, y_test),
                    callbacks=[early_stopping])

# Hiển thị kết quả huấn luyện
print("Training completed.")
print(f"Training Loss: {history.history['loss']}")
print(f"Training Accuracy: {history.history['accuracy']}")
print(f"Validation Loss: {history.history['val_loss']}")
print(f"Validation Accuracy: {history.history['val_accuracy']}")