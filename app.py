import os
import numpy as np
import cv2
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.resnet50 import preprocess_input
from werkzeug.utils import secure_filename
from valid import validate_image

app = Flask(__name__)
project_root = os.path.dirname(os.path.abspath(__file__))
model = load_model(os.path.join(project_root, 'Braintumor10EpochsCategorical.h5'))
print('Model loaded. Check http://127.0.0.1:5000/')

UPLOAD_FOLDER = os.path.join(project_root, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_className(classNo):
    return "Normal" if classNo == 0 else "Brain Tumor"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Validate image before predicting
        if not validate_image(file_path):
            os.remove(file_path)
            return render_template('index.html', error='Ảnh không hợp lệ. Vui lòng upload ảnh có kích thước tối thiểu 224×224 pixel.')

        # Load and preprocess image
        image = cv2.imread(file_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (224, 224))
        image = np.array(image, dtype=np.float32)
        input_img = np.expand_dims(image, axis=0)
        input_img = preprocess_input(input_img)
        
        # Predict
        result = model.predict(input_img)
        class_no = np.argmax(result)
        class_name = get_className(class_no)
        
        return render_template('result.html', result=class_name, filename=filename)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
