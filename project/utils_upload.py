from django.utils import timezone
import os
import json


def message_image(instance, filename):
    # Генерация нового имени файла
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    new_filename = f'MessageImage_{timestamp}_{filename}'

    # Путь для сохранения файла в папке "Topic"
    upload_path = os.path.join("MessageImage/", new_filename)

    return upload_path


def save_default():
    file_path = "project/TaskDataCalculate.json"
    try:
        with open(file_path, "r") as json_file:
            default_data = json.load(json_file)
    except FileNotFoundError:
        # Если файл не найден, создаем пустой список
        default_data = []
    return default_data
