from rest_framework import serializers
from .models import MyUser, Teams
from project.models import Task, Project, Region


class MyUserSerializer(serializers.ModelSerializer):
    tasks_completed = serializers.IntegerField(read_only=True)
    total_points = serializers.FloatField(read_only=True)

    class Meta:
        model = MyUser
        fields = ['id', 'first_name', 'last_name', 'tasks_completed', 'total_points']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['id', 'username', 'role', 'first_name', 'last_name', 'phone_number', 'link_telegram']
        ref_name = 'DjoserUser'


class UserTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['id', 'first_name', 'last_name']
        ref_name = 'DjoserUser1'


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['name']


class ProjectTeamleadSerializer(serializers.ModelSerializer):
    region = RegionSerializer()

    class Meta:
        model = Project
        fields = ('id', 'project_name', 'region', 'built', 'exterior_status')


class TeamsSerializer(serializers.ModelSerializer):
    teamlead = UserSerializer(many=False)  # Assuming teamlead is a ForeignKey to the User model
    employees = UserSerializer(many=True)

    class Meta:
        model = Teams
        fields = '__all__'


class TeamsCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Teams
        fields = '__all__'
