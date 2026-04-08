import os
import sys

def get_className(classNo):
    return "Normal" if classNo == 0 else "Brain Tumor"

if __name__ == '__main__':
    if not os.path.exists('/uploads/'):
        os.makedirs('/uploads/')
    
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

    # app.run(debug=True)
