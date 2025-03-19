from django.utils import timezone
import os
from django.core.exceptions import ValidationError


def message_correcting_image(instance, file):
    if file == "blob":
        ext = ".jpg"  # расширение по умолчанию для бинарных файлов
    else:
        filename = file
        ext = os.path.splitext(filename)[1]  # получаем расширение файла

    # Генерация нового имени файла
    timestamp = timezone.now().strftime('%d_%m_%Y__%H_%M_%S')
    new_filename = f'id{instance.id}_{timestamp}{ext}'
    print(instance.id)
    # Путь для сохранения файла в папке "Render"
    upload_path = os.path.join("MessageCorrectingImage", new_filename)

    return upload_path


def render_image(instance, file):
    # Если file - это Blob (байтовый поток), используем дефолтное имя файла
    if file == "blob":
        ext = ".jpg"  # расширение по умолчанию для бинарных файлов
    else:
        filename = file
        ext = os.path.splitext(filename)[1]  # получаем расширение файла

    # Генерация нового имени файла
    timestamp = timezone.now().strftime('%d_%m_%Y__%H_%M_%S')
    print(instance.id)
    new_filename = f'{instance.project_id.title}_id{instance.id}_{timestamp}{ext}'

    # Путь для сохранения файла в папке "Render"
    upload_path = os.path.join("Render", new_filename)

    return upload_path


def floor_plan_render_image(instance, filename):
    # Генерация нового имени файла
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    new_filename = f'id{instance.id}_{timestamp}_{filename}'

    # Путь для сохранения файла в папке "Topic"
    upload_path = os.path.join("FloorPlanRender/", new_filename)

    return upload_path


def project_file(instance, filename):
    # Получаем расширение загружаемого файла
    ext = os.path.splitext(filename)[-1]

    # Генерация нового имени файла
    timestamp = timezone.now().strftime('%d_%m_%Y__%H_%M_%S')
    new_filename = f'{instance.project_file_id.title}_{timestamp}_{ext}'

    # Путь для сохранения файла в папке "Topic"
    upload_path = os.path.join("ProjectFile/", new_filename)

    return upload_path
