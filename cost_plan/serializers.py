from django.db.models import TextField
from rest_framework import serializers
from .models import *

class TariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = '__all__'  # Включить все поля модели


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'  # Включить все поля модели


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'  # Включить все поля модели


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'  # Включить все поля модели


'''     Data    '''
class FullTypeDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeData
        fields = '__all__'


class FullTaskGroupDataSerializer(serializers.ModelSerializer):
    task_data = FullTypeDataSerializer(many=True)
    class Meta:
        model = TaskGroupData
        fields = '__all__'


class FullTaskDataSerializer(serializers.ModelSerializer):
    task_group_data = FullTaskGroupDataSerializer(many=True)

    class Meta:
        model = TaskData
        fields = '__all__'


class FullProductDataSerializer(serializers.ModelSerializer):
    task_group_data = FullTaskGroupDataSerializer(many=True)
    task_data = FullTaskDataSerializer(many=True)
    type = FullTypeDataSerializer(many=True)

    class Meta:
        model = ProductData
        fields = '__all__'


class TaskGroupDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskGroupData
        fields = '__all__'


class TaskDataDataSerializer(serializers.ModelSerializer):
    task_group_data = TaskGroupDataSerializer(many=True, read_only=True)

    class Meta:
        model = TaskData
        fields = "__all__"


class ProductDataSerializer(serializers.ModelSerializer):
    type = FullTypeDataSerializer(many=True)
    task_data = FullTaskDataSerializer(many=True)
    class Meta:
        model = ProductData
        fields = '__all__'


''' Calculate '''

class FullTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class FullProductSerializer(serializers.ModelSerializer):
    type = FullTypeDataSerializer()
    class Meta:
        model = Product
        fields = '__all__'


class FullProjectSerializer(serializers.Serializer):
    products = FullProductSerializer(many=True)

    class Meta:
        model = Project
        fields = '__all__'
