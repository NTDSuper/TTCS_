import os
import cv2
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
import tensorflow as tf
from log import file_logging_callback


print(f"TensorFlow version: {tf.__version__}")

# Tham số
INPUT_SIZE = 224  # ResNet50 yêu cầu đầu vào kích thước 224x224
BATCH_SIZE = 32
EPOCHS = 100
LEARNING_RATE = 1e-4

# Đọc dữ liệu
project_root = os.path.dirname(os.path.abspath(__file__))
image_directory = os.path.join(project_root, 'datasets')
no_tumor_dir = os.path.join(image_directory, 'no')
yes_tumor_dir = os.path.join(image_directory, 'yes')

if not os.path.isdir(no_tumor_dir) or not os.path.isdir(yes_tumor_dir):
    raise FileNotFoundError(
        f"Không tìm thấy thư mục dữ liệu. Kiểm tra lại: '{no_tumor_dir}' và '{yes_tumor_dir}'"
    )

no_tumor_images = os.listdir(no_tumor_dir)
yes_tumor_images = os.listdir(yes_tumor_dir)

dataset = []
labels = []

for image_name in no_tumor_images:
    if image_name.lower().endswith(('.jpg', '.jpeg', '.png')):
        image_path = os.path.join(no_tumor_dir, image_name)
        image = cv2.imread(image_path)
        if image is not None:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.resize(image, (INPUT_SIZE, INPUT_SIZE))
            dataset.append(image)
            labels.append(0)

for image_name in yes_tumor_images:
    if image_name.lower().endswith(('.jpg', '.jpeg', '.png')):
        image_path = os.path.join(yes_tumor_dir, image_name)
        image = cv2.imread(image_path)
        if image is not None:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.resize(image, (INPUT_SIZE, INPUT_SIZE))
            dataset.append(image)
            labels.append(1)

dataset = np.array(dataset, dtype=np.float32)
labels = np.array(labels)

if len(dataset) == 0:
    raise ValueError("Không có ảnh hợp lệ trong datasets/no và datasets/yes")

# Tiền xử lý đúng chuẩn ResNet50
dataset = preprocess_input(dataset)

# Split dữ liệu thành train và test
x_train, x_test, y_train, y_test = train_test_split(
    dataset,
    labels,
    test_size=0.2,
    random_state=42,
    stratify=labels,
)

class_weights = compute_class_weight(class_weight='balanced', classes=np.unique(y_train), y=y_train)
class_weight_dict = {i: w for i, w in enumerate(class_weights)}

# Tạo Data Augmentation
datagen = ImageDataGenerator(
    rotation_range=15,
    width_shift_range=0.1,
    height_shift_range=0.1,
    zoom_range=0.15,
    horizontal_flip=True,
    fill_mode='nearest'
)

# Sử dụng mô hình ResNet50 pre-trained
base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(INPUT_SIZE, INPUT_SIZE, 3))

# Đóng băng các lớp của mô hình base
for layer in base_model.layers:
    layer.trainable = False

# Mở fine-tune một phần các lớp cuối để tăng độ chính xác
for layer in base_model.layers[-30:]:
    if not isinstance(layer, tf.keras.layers.BatchNormalization):
        layer.trainable = True

# Tạo mô hình mới với các lớp tùy chỉnh
model = Sequential([
    base_model,
    GlobalAveragePooling2D(),
    Dense(256, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(1e-4)),
    Dropout(0.5),
    Dense(2, activation='softmax')
])

# Biên dịch mô hình
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE),
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Cơ chế Early Stopping
early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=4, restore_best_weights=True)
reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.3, patience=2, min_lr=1e-7, verbose=1)
checkpoint_path = os.path.join(project_root, 'Braintumor10EpochsCategorical.h5')
model_checkpoint = tf.keras.callbacks.ModelCheckpoint(
    checkpoint_path,
    monitor='val_accuracy',
    mode='max',
    save_best_only=True,
    verbose=1,
)

# Huấn luyện mô hình và lưu lịch sử
history = model.fit(datagen.flow(x_train, y_train, batch_size=BATCH_SIZE),
                    epochs=EPOCHS,
                    validation_data=(x_test, y_test),
                    class_weight=class_weight_dict,
                    callbacks=[early_stopping, reduce_lr, model_checkpoint, file_logging_callback])

# Hiển thị kết quả huấn luyện
print("Training completed.")
print(f"Training Loss: {history.history['loss']}")
print(f"Training Accuracy: {history.history['accuracy']}")
print(f"Validation Loss: {history.history['val_loss']}")
print(f"Validation Accuracy: {history.history['val_accuracy']}")