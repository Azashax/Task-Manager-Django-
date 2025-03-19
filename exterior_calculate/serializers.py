from rest_framework import serializers
from .models import ProjectExterior, Building, BuildingObjects, Floors, Details,\
    TopologyHard, ProjectsImage
from User.serializers import UserSerializer


class ProjectsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectsImage
        fields = '__all__'


class TopologyHardSerializer(serializers.ModelSerializer):
    screenshots = ProjectsImageSerializer(many=True, read_only=True)

    class Meta:
        model = TopologyHard
        fields = '__all__'


''' Projects '''
class ProjectCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectExterior
        fields = '__all__'

    def create(self, validated_data):
        if self.context['request'].user.role == "ExTeamlead":
            validated_data['project_ex_teamlead_user'] = self.context['request'].user
        return super(ProjectCreateSerializer, self).create(validated_data)


class ProjectListSerializer(serializers.ModelSerializer):
    project_ex_teamlead_user = UserSerializer()

    class Meta:
        model = ProjectExterior
        fields = '__all__'


class ProjectUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectExterior
        fields = ['project_name', 'link_clickup', 'link_cet3', 'project_type', 'description', 'texture', 'calculated']


''' Buildings '''
class BuildingListCreateSerializer(serializers.ModelSerializer):
    screenshots = ProjectsImageSerializer(many=True, read_only=True)

    class Meta:
        model = Building
        fields = '__all__'


''' Objects '''
class ObjectsListCreateSerializer(serializers.ModelSerializer):
    screenshots = ProjectsImageSerializer(many=True, read_only=True)
    # topology_hard = TopologyHardSerializer(many=True)

    class Meta:
        model = BuildingObjects
        fields = '__all__'


''' Floors '''
class FloorsListCreateSerializer(serializers.ModelSerializer):
    screenshots = ProjectsImageSerializer(many=True, read_only=True)
    # topology_hard = TopologyHardSerializer(many=True)

    class Meta:
        model = Floors
        fields = '__all__'


''' Details '''
class DetailsListCreateSerializer(serializers.ModelSerializer):
    screenshots = ProjectsImageSerializer(many=True, read_only=True)
    # topology_hard = TopologyHardSerializer(many=True)

    class Meta:
        model = Details
        fields = '__all__'