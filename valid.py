from PIL import Image

def validate_image(image_path):
    try:
        with Image.open(image_path) as img:
            # Kiểm tra kích thước của hình ảnh
            if img.size[0] < 64 or img.size[1] < 64:
                return False
            # Có thể thêm các kiểm tra khác nếu cần
        return True
    except Exception as e:
        print(f"Image validation error: {e}")
        return False
