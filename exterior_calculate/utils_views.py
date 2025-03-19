from .models import ProjectsImage, TopologyHard
from rest_framework.response import Response
from rest_framework import status
import time


def process_patch_request(instance, serializer_class, request):
    screenshots_to_add = request.FILES.getlist('new_screenshots', None)  # Новые изображения
    screenshots_to_delete = request.data.getlist('remove_screenshots', [])

    # Создаём копию данных без ключей, относящихся к изображениям
    data = request.data.copy()
    data.pop("new_screenshots", None)
    data.pop("remove_screenshots", None)

    # Если поле `data` существует и является списком
    if "data" in data:
        raw_data = data["data"]
        if isinstance(raw_data, list):  # Если `data` — это список
            try:
                data["data"] = raw_data[0]  # Берём первый элемент
            except IndexError:
                return Response({"error": "'data' field is empty"}, status=400)

    # Удаляем пустые поля
    if not data.get("topology_hard"):
        data.pop("topology_hard", None)
    data.pop("screenshots", None)

    serializer = serializer_class(instance, data=data, partial=True)
    if serializer.is_valid():
        instance = serializer.save()

        # Добавляем новые изображения
        for image in screenshots_to_add:
            object_image = ProjectsImage.objects.create(img=image)
            instance.screenshots.add(object_image)
            time.sleep(2)
        # Удаляем указанные изображения
        ProjectsImage.objects.filter(id__in=screenshots_to_delete).delete()

        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# def topology_type_objects(building_object_instance, request):
#     print(request.data)
#     print(request.data.get("objects"))
#     print(request.FILES)
#     objects_data = json.loads(request.data.get("objects"))  # Парсим JSON из запроса
#     files = request.FILES  # Все файлы из запроса
#
#     for index, obj_data in enumerate(objects_data):
#         # Создаем объект `TopologyHard`
#         new_object = TopologyHard.objects.create(
#             title=obj_data["title"],
#             description=obj_data.get("description", ""),
#             data=obj_data["data"],
#         )
#         print(index)
#         print(obj_data)
#         print(new_object)
#         screenshots = files.getlist(f"objects[{index}][screenshots]")
#         for screenshot in screenshots:
#             print(screenshot)
#             image_instance = ProjectsImage.objects.create(img=screenshot)
#             new_object.screenshots.add(image_instance)
#         # Привязываем к основному объекту
#         building_object_instance.topology_hard.add(new_object)

