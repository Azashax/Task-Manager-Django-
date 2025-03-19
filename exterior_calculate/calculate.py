from functools import reduce
from .models import AdditionalStructure


def calculate_time(data, additional_structure):
    fields = [
        ("geometry_straight", additional_structure.geometry_straight),
        ("geometry_curve", additional_structure.geometry_curve),
        ("topology_cyclic", additional_structure.topology_cyclical),
        ("topology_chaotic", additional_structure.topology_chaotic),
        ("deformations_easy", additional_structure.deformation_easy),
        ("deformations_hard", additional_structure.deformation_hard),
        ("symmetric", additional_structure.symmetry, True),
        ("copy", additional_structure.copy),
        ("cyclic_copy", additional_structure.cyclic_copy),
        ("arabian_logo", additional_structure.arabian_logo),
        ("logo", additional_structure.logo),
        ("primitive", additional_structure.primitive),
        ("furniture", additional_structure.furniture),
        ("railing", additional_structure.railing),
        ("railing_curve", additional_structure.railing_curve),
        ("staircase_straight", additional_structure.staircase_straight),
        ("staircase_curves", additional_structure.staircase_curves),
    ]

    # Проверяем, что data – это словарь
    if not isinstance(data, dict):
        raise ValueError("Data is not in the expected dictionary format.")

    # Рассчитываем итоговое время
    return sum(
        data.get(field, 0) * multiplier if not is_bool else int(data.get(field, False)) * multiplier
        for field, multiplier, *is_bool in fields
    )


def calculate_object_time(building_object, additional_structure):
    total_sum = calculate_time(building_object.data, additional_structure)
    for floor in building_object.floors.all():
        print(floor.data)
        total_sum += calculate_time(floor.data, additional_structure)
        for detail in floor.details.all():
            total_sum += calculate_time(detail.data, additional_structure)
    return total_sum


def calculate_project_time(project):
    total_low, total_midl, total_high = 0, 0, 0
    additional_structure = AdditionalStructure.load()
    if not additional_structure:
        raise ValueError("Additional structure configuration is missing.")
    buildings = project.buildings.all()
    for building in buildings:
        building_objects = building.building_objects.all()
        building_time = sum(
            calculate_object_time(obj, additional_structure) for obj in building_objects
        )
        if building.mid_poly:
            total_midl += building_time
        else:
            total_high += building_time

    study_info = additional_structure.study_info
    if not isinstance(study_info, (int, float)):
        raise ValueError("Invalid value for study_info.")

    return int(total_low), int(total_midl * study_info), int(total_high * study_info)






""" функция для форматирования секунды в стандартный вариант"""
# def seconds_to_days_hours_minutes_seconds(seconds):
#     minutes = seconds // 60
#     hours1 = minutes // 60
#     remaining_minutes = minutes % 60
#     days = hours1 // 8
#     hours = hours1 % 8
#     remaining_seconds = seconds % 60
#     time = f"{days}d {hours}h {remaining_minutes}m {remaining_seconds}s"
#     point = hours1 + round((remaining_minutes * 60 + remaining_seconds) / 3600, 2)
#     return time, round(point, 2)

""" расчёт времени для хъард топологий """
# # Получаем все связанные объекты TopologyHard, связанные с ObjectsDetails
# related_topology_hard = objects_detail.topology_hard.all()
#
# # Проходимся по каждому объекту TopologyHard, связанному с ObjectsDetails
# for related_topology_hard_object in related_topology_hard:
#     total_sum += (
#             int(related_topology_hard_object.geometry_straight) * additional_structure.straight +
#             int(related_topology_hard_object.geometry_curve) * additional_structure.curves +
#             # int(related_topology_hard_object.primitive) * additional_structure.primitive +
#             int(related_topology_hard_object.deformation) * additional_structure.deformation_easy +
#             int(related_topology_hard_object.deformation_hard) * additional_structure.deformation_hard +
#             int(1 if related_topology_hard_object.symmetric else 0) * additional_structure.symmetry +
#             int(related_topology_hard_object.copy) * additional_structure.copy
#     )