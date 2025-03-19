import os


def task_files(instance, filename):
    # Генерация нового имени файла
    new_filename = f'{instance.project.title}_{instance.id}_{filename}'

    upload_path = os.path.join("Interior/3DModelFile/", new_filename)

    return upload_path


def task_images(instance, filename):
    # Генерация нового имени файла
    new_filename = f'{instance.project.title}_{instance.id}_{filename}'

    upload_path = os.path.join("Interior/FlorPlanImages/", new_filename)

    return upload_path


def message_images(instance, filename):
    # Проверка, что task_message и его task и project существуют
    task_message = instance.task_message
    task = task_message.task if task_message else None
    project = task.project if task else None

    # Формируем части имени файла на основе доступных данных
    project_title = project.title if project else "unknown_project"
    task_id = task.id if task else "unknown_task"
    task_message_id = task_message.id if task_message and task_message.id else "new_message"

    # Генерируем новое имя файла
    new_filename = f'{project_title}_{task_id}_{task_message_id}_{filename}'

    # Формируем путь загрузки
    upload_path = os.path.join("Interior/Task/Message/", new_filename)

    return upload_path
