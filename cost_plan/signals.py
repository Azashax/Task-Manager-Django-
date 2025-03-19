from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Project, Product, Task, Tariff, TypeData


# def create_tasks_for_product(product, task_group_data_items):
#     """
#     Создает задачи для указанного продукта и назначает TaskData.
#     Использует bulk_create() для повышения производительности.
#     """
#     tasks_to_create = []
#     print("A6")
#     for task_group_data in task_group_data_items:
#         print("A7")
#         for task_data in task_group_data.task_data.all():
#             tasks_to_create.append(Task(
#                 title=task_data.title,
#                 product=product,
#                 task_data=task_data
#             ))
#     print("A8")
#     if tasks_to_create:
#         Task.objects.bulk_create(tasks_to_create)
#         print("A9")


def create_products_for_project(instance):
    """
    Создает продукты и задачи для нового проекта на основе тарифа.
    """
    tariff = Tariff.objects.filter(title=instance.tariff).prefetch_related(
        'product_data__task_group_data__task_data').first()

    if not tariff:
        return  # Если тариф не найден, выходим

    products_to_create = []
    product_task_mapping = {}
    print('A1')
    # Создаем продукты
    for product_item in tariff.product_data.all():
        task_group_value = {task_group_data.title: 0 for task_group_data in product_item.task_group_data.all()}
        print('A2')
        product = Product(
            title=product_item.title,
            project=instance,
            fields=task_group_value,  # JSONField
            type=TypeData.objects.get(title="small")
        )
        products_to_create.append(product)
        product_task_mapping[product.title] = product_item.task_group_data.all()
        print('A3')

    if products_to_create:
        created_products = Product.objects.bulk_create(products_to_create)
        # print('A4')
        # # Создаем задачи для каждого продукта
        # for product in created_products:
        #     create_tasks_for_product(product, product_task_mapping[product.title])
        # print('A5')

# Сигнал для создания продуктов и задач
@receiver(post_save, sender=Project)
def create_products_and_tasks(sender, instance, created, **kwargs):
    if created:
        create_products_for_project(instance)
