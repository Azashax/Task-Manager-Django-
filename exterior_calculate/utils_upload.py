from django.utils import timezone
import os
from django.core.exceptions import ValidationError


def validate_file_extension(value):
    if not value.name.endswith('.zip'):
        raise ValidationError(u'Ошибка: Файл не является ZIP-архивом.')


def project_texture(instance, filename):
    # Генерация нового имени файла
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    new_filename = f'project_texture_{timestamp}_{filename}'

    # Путь для сохранения файла в папке "Topic"
    upload_path = os.path.join("project_texture", new_filename)

    return upload_path


def screenshots(instance, filename):
    # Генерация нового имени файла
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    new_filename = f'screenshots_{timestamp}_{filename}'

    # Путь для сохранения файла в папке "Topic"
    upload_path = os.path.join("screenshots/", new_filename)

    return upload_path


