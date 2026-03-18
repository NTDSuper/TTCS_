from PIL import Image

MODEL_INPUT_WIDTH = 224
MODEL_INPUT_HEIGHT = 224

def validate_image(image_path):
    try:
        with Image.open(image_path) as img:
            # Kiểm tra kích thước của hình ảnh
            if img.size[0] < MODEL_INPUT_WIDTH or img.size[1] < MODEL_INPUT_HEIGHT:
                return False
            # Có thể thêm các kiểm tra khác nếu cần
        return True
    except Exception as e:
        print(f"Image validation error: {e}")
        return False
