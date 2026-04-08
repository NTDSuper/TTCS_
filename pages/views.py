# views.py
import os
from pathlib import Path
import sys
import numpy as np
from PIL import Image
from io import BytesIO
import base64
import cv2
from keras.models import load_model
from tensorflow.keras.applications.resnet50 import preprocess_input
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required # Import decorator này
from django.conf import settings # Cần import settings để tham chiếu AUTH_USER_MODEL

# Tải model - Đảm bảo đường dẫn này là đúng và file có thể truy cập
model = None
try:
    # Sử dụng settings.BASE_DIR để xây dựng đường dẫn tuyệt đối đến file model
    # Điều chỉnh 'Braintumor10EpochsCategorical.h5' nếu file ở thư mục con
    model_path = Path(settings.BASE_DIR) / 'Braintumor10EpochsCategorical.h5'
    if model_path.exists():
        model = load_model(str(model_path))
        print(f"Model loaded successfully from {model_path}.")
    else:
        print(f"Model file not found at {model_path}.")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None # Xử lý trường hợp model không tải được


from django.views.generic import TemplateView
from django.shortcuts import render, redirect
# Import model DiagnosisHistory
from pages.models import DiagnosisHistory
# Import timezone để xử lý ngày giờ
from django.utils.timezone import now
# Import os.path để lấy tên file
import os.path


# Các View đơn giản chỉ hiển thị template (yêu cầu đăng nhập)
class HomePageView(LoginRequiredMixin, TemplateView):
    login_url = '/accounts/login/'
    template_name = "pages/home.html"

class ContactPageView(LoginRequiredMixin, TemplateView):
    login_url = '/accounts/login/'
    template_name = "pages/contact.html"

class FAQPageView(LoginRequiredMixin, TemplateView):
    login_url = '/accounts/login/'
    template_name = "pages/faq.html"


def get_className(classNo):
    return "Normal" if classNo == 0 else "Brain Tumor"

def image_to_base64(image):
    """Chuyển đối tượng PIL Image thành chuỗi base64."""
    if image is None:
        return ""
    if image.mode not in ('RGB', 'RGBA'):
        image = image.convert('RGB')
    buff = BytesIO()
    try:
         image.save(buff, format="PNG")
    except IOError:
         try:
             image.save(buff, format="JPEG")
         except Exception as e:
             print(f"Error saving image to buffer: {e}")
             return ""

    img_str = base64.b64encode(buff.getvalue()).decode("utf-8")
    return img_str

# View xử lý POST request để dự đoán
@login_required(login_url='/accounts/login/') # Yêu cầu đăng nhập cho view này
def predict(request):
    # Chỉ xử lý yêu cầu POST có file
    if request.method != 'POST' or not request.FILES:
         # Nếu không phải POST hoặc không có file, chuyển hướng về trang diagnose
         # Truyền thông báo lỗi nếu cần thiết, và cả lịch sử của user đó
         user_history = DiagnosisHistory.objects.filter(user=request.user).order_by('-date')
         for item in user_history:
             item.filename_display = os.path.basename(item.file.name) if item.file and item.file.name else "No file"
         return render(request, "pages/diagnose.html", {
             'error': 'Yêu cầu không hợp lệ. Vui lòng tải ảnh lên từ trang chẩn đoán.',
             'history': user_history
         })

    file = request.FILES.get('xray')

    if not file:
        # Chuyển hướng về trang diagnose và hiển thị lỗi nếu không có file
        # Trước khi render, lấy lịch sử CỦA USER HIỆN TẠI để hiển thị trên trang diagnose
        user_history = DiagnosisHistory.objects.filter(user=request.user).order_by('-date')
        for item in user_history:
            item.filename_display = os.path.basename(item.file.name) if item.file and item.file.name else "No file"
        return render(request, "pages/diagnose.html", {
            'error': 'Vui lòng chọn một tệp ảnh.',
            'history': user_history # Truyền lịch sử chỉ của user hiện tại
        })

    class_name = "Không xác định"
    image64 = ""

    try:
        file.seek(0) # Reset con trỏ file
        image_bytes = file.read()
        image_np = np.frombuffer(image_bytes, np.uint8)
        image_cv2 = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        if image_cv2 is None:
             print("CV2 failed to decode image.")
             user_history = DiagnosisHistory.objects.filter(user=request.user).order_by('-date')
             for item in user_history:
                item.filename_display = os.path.basename(item.file.name) if item.file and item.file.name else "No file"
             return render(request, "pages/diagnose.html", {
                 'error': 'Không thể giải mã tệp ảnh. Vui lòng kiểm tra định dạng.',
                 'history': user_history
                 })

        image_cv2_rgb = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2RGB)
        image_resized = cv2.resize(image_cv2_rgb, (224, 224))
        image_np_array = np.array(image_resized, dtype=np.float32)
        input_img = np.expand_dims(image_np_array, axis=0)
        input_img = preprocess_input(input_img)

        if model:
            print("Performing prediction...")
            result_prediction = model.predict(input_img)
            print(f"Prediction result: {result_prediction}")
            class_no = np.argmax(result_prediction)
            class_name = get_className(class_no)
            print(f"Predicted class: {class_name} (Class No: {class_no})")
        else:
            class_name = "Lỗi: Model không được tải. Không thể chẩn đoán."
            print(class_name)
            user_history = DiagnosisHistory.objects.filter(user=request.user).order_by('-date')
            for item in user_history:
                item.filename_display = os.path.basename(item.file.name) if item.file and item.file.name else "No file"
            return render(request, "pages/diagnose.html", {
                'error': class_name,
                'history': user_history
                })


        # Chuẩn bị ảnh để hiển thị (sử dụng đối tượng file gốc cho PIL)
        file.seek(0) # Reset con trỏ file
        file_copy_for_pil = BytesIO(file.read())
        image_pil = Image.open(file_copy_for_pil)
        image64 = image_to_base64(image_pil)

        # LƯU LỊCH SỬ - Thêm trường user=request.user
        file.seek(0) # Reset con trỏ file lần cuối trước khi Django lưu
        history_record = DiagnosisHistory(
                user=request.user, # <--- Gán người dùng hiện tại vào đây
                file= file,
                result= class_name,
            )
        history_record.save()

        # --- LẤY VÀ CHUẨN BỊ LỊCH SỬ CỦA USER HIỆN TẠI CHO TRANG RESULT ---
        # Lấy tất cả các bản ghi lịch sử *chỉ của người dùng hiện tại*
        user_history = DiagnosisHistory.objects.filter(user=request.user).order_by('-date')

        # Thêm thuộc tính filename_display cho mỗi mục lịch sử
        for item in user_history:
            if item.file and item.file.name:
                item.filename_display = os.path.basename(item.file.name)
            else:
                item.filename_display = "No file"

        # Render trang kết quả, truyền lịch sử CỦA USER HIỆN TẠI
        return render(request, "pages/result.html", {
            'result': class_name,
            'image64': image64,
            'history': user_history # <--- Truyền lịch sử chỉ của user hiện tại
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Prediction error: {e}")
        # Render lại trang chẩn đoán với thông báo lỗi và lịch sử CỦA USER HIỆN TẠI
        user_history = DiagnosisHistory.objects.filter(user=request.user).order_by('-date')
        for item in user_history:
            item.filename_display = os.path.basename(item.file.name) if item.file and item.file.name else "No file"
        return render(request, "pages/diagnose.html", {
            'error': f'Đã xảy ra lỗi trong quá trình xử lý ảnh: {e}',
            'history': user_history # Truyền lịch sử chỉ của user hiện tại
        })


# Hàm này được sử dụng cho đường dẫn /diagnose/ (GET request)
@login_required(login_url='/accounts/login/') # Yêu cầu đăng nhập cho view này
def diagnose(request):
    # Lấy lịch sử chẩn đoán CHỈ CỦA USER HIỆN TẠI để hiển thị trên trang diagnose ban đầu
    user_history = DiagnosisHistory.objects.filter(user=request.user).order_by('-date')

    # Thêm thuộc tính filename_display cho mỗi mục lịch sử
    for item in user_history:
        if item.file and item.file.name:
            item.filename_display = os.path.basename(item.file.name)
        else:
            item.filename_display = "No file"

    # Truyền biến 'history' (chứa lịch sử của user hiện tại) vào template diagnose.html
    return render(request, 'pages/diagnose.html', {'history': user_history})