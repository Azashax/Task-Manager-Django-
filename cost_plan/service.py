from django.db import transaction, DatabaseError, IntegrityError
from .models import Product, TypeData, Task, Task, SubTask, UserProduct
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist


def products_update_type_fields(products_data):

    for product in products_data:
        product_id = product.get("id")
        if product_id:
            product_obj = Product.objects.get(id=product_id)
            product_obj.fields = product["fields"]
            product_obj.type_id = product["type"].get("id") if product.get("type") else None
            product_obj.save()
        else:
            Product.objects.create(
                project_id=product["project"],
                title=product["title"],
                fields=product["fields"],
                type_id=product["type"].get("id") if product.get("type") else None,
            )
    return "success"


def products_deleted(del_products):
    for product_id in del_products:
        try:
            product = Product.objects.get(id=product_id)
            product.delete()
        except ObjectDoesNotExist:
            print("not product")


def tasks_update_time_money(tasks_data):
    tasks_to_update = []
    errors = []  # Логирование ошибок

    for key, params in tasks_data.items():
        task_id_parts = key.split("-")

        # Проверяем корректность ключа
        if len(task_id_parts) < 2:
            errors.append({"task_key": key, "error": "Invalid task key format"})
            continue

        task_id = task_id_parts[1]
        time = params.get("time")

        # Проверяем корректность данных
        if not task_id.isdigit() or not isinstance(time, (int, float)):
            errors.append({"task_id": task_id, "error": "Invalid time format"})
            continue

        try:
            task = Task.objects.get(id=int(task_id))
            if task.duration != time:  # Проверяем, изменилось ли значение
                task.duration = time
                tasks_to_update.append(task)
        except Task.DoesNotExist:
            errors.append({"task_id": task_id, "error": "Task not found"})
            continue

    # Обновляем все задачи одним запросом
    if tasks_to_update:
        try:
            with transaction.atomic():
                Task.objects.bulk_update(tasks_to_update, ["duration"])
            return {"status": "success", "updated_count": len(tasks_to_update), "errors": errors}
        except DatabaseError as e:
            return {"status": "error", "message": str(e), "errors": errors}

    return {"status": "success", "updated_count": 0, "errors": errors}



""" Логика автоматического создания SubTask и назначения сотрудников  """


# # Пример функции для проверки пересечения времени двух интервалов
# def is_overlapping(desired_start, desired_end, existing_start, existing_end):
#     return not (desired_end <= existing_start or desired_start >= existing_end)
#
#
# # Функция, которая проверяет, свободен ли сотрудник в момент desired_start
# def is_candidate_free(candidate, desired_start, desired_end, project):
#     # Получаем все субтаски кандидата в рамках данного проекта
#     candidate_subtasks = SubTask.objects.filter(
#         user=candidate,
#         parent_task__product=project,
#         status__in=['todo', 'in_progress']
#     )
#     for subtask in candidate_subtasks:
#         if is_overlapping(desired_start, desired_end, subtask.start_time, subtask.end_time):
#             return False
#     return True
#
#
# # Функция для поиска свободного кандидата или, если не найден, ближайшего по освобождению
# def select_candidate(candidates, desired_start, time_spent, project):
#     desired_end = desired_start + timedelta(minutes=time_spent)
#     free_candidate = None
#     earliest_free_candidate = None
#     earliest_free_time = None
#
#     for candidate in candidates:
#         if is_candidate_free(candidate, desired_start, desired_end, project):
#             # Если кандидат свободен в заданный интервал, возвращаем его сразу
#             return candidate, desired_start, 0  # waiting_time = 0
#
#         # Если кандидат не свободен, находим время, когда он освободится
#         candidate_subtasks = SubTask.objects.filter(
#             user=candidate,
#             parent_task__product=project,
#             status__in=['todo', 'in_progress']
#         ).order_by('end_time')
#
#         if candidate_subtasks.exists():
#             candidate_free_time = candidate_subtasks.last().end_time
#         else:
#             candidate_free_time = desired_start  # Теоретически должен быть свободен
#
#         # Выбираем кандидата, который освободится раньше
#         if earliest_free_time is None or candidate_free_time < earliest_free_time:
#             earliest_free_time = candidate_free_time
#             earliest_free_candidate = candidate
#
#     # Рассчитываем waiting_time
#     waiting_time = (earliest_free_time - desired_start).total_seconds() / 60  # в минутах
#     return earliest_free_candidate, earliest_free_time, waiting_time
#
#
# @transaction.atomic
# def assign_subtasks(project):
#     # Получаем задачи проекта, сортируем по позиции (если поле position есть)
#     tasks = Task.objects.filter(product=project).order_by('position')
#
#     for task in tasks:
#         # Определяем требуемую роль для задачи
#         required_role = getattr(task.task_data, 'required_role', None)
#         if required_role is None:
#             continue  # Если роль не задана, пропускаем задачу
#
#         # Определяем количество субтасков, которые нужно создать
#         # Если several True → количество = task.total (за вычетом уже созданных, если нужно)
#         # Если several False → создаём только 1 субтаск
#         existing_subtasks = task.subtasks.filter(status__in=['todo', 'in_progress']).count()
#         if task.several:
#             num_to_create = task.total - existing_subtasks
#         else:
#             num_to_create = 1 if existing_subtasks == 0 else 0
#
#         # Получаем кандидатов по требуемой роли
#         candidates = list(UserProduct.objects.filter(role=required_role).order_by('id'))
#
#         # Для каждого субтаска определяем время выполнения
#         # Предположим, что task.duration содержит время выполнения в минутах
#         time_spent = task.duration if task.duration else 60  # значение по умолчанию
#
#         for i in range(num_to_create):
#             # Желаемое время старта можно задать как текущее время или смещённое с учётом предыдущих субтасков
#             desired_start = timezone.now()
#
#             # Для каждого нового субтаска можно дополнительно искать свободного пользователя среди субтасков проекта
#             candidate, actual_start, waiting_time = select_candidate(candidates, desired_start, time_spent, project)
#
#             actual_end = actual_start + timedelta(minutes=time_spent)
#
#             # Создаем субтаск
#             SubTask.objects.create(
#                 parent_task=task,
#                 title=f"Subtask {existing_subtasks + i + 1} for {task.title}",
#                 user=candidate,
#                 start_time=actual_start,
#                 end_time=actual_end,
#                 time_spent=time_spent,
#                 waiting_time=waiting_time,  # если у модели SubTask есть такое поле
#                 status='todo'
#             )
