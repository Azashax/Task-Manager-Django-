from django.urls import path, include
from .views import *

project_patterns = [
    path('', ProjectListCreateAPI.as_view(), name='list'),
    path('<int:project_id>/', ProjectUpdateAPI.as_view(), name='details'),
    path('<int:project_id>/calculate/', ProjectsCalculateView.as_view(), name='calculate'),
    path('<int:project_id>/download/', DownloadProjectExteriorAPI.as_view(), name='download'),
]

building_patterns = [
    path('<int:project_id>/', BuildingListCreateAPI.as_view(), name='list'),
    path('<int:building_id>/details/', BuildingUpdateDeleteDetailsAPI.as_view(), name='building-detail'),
]

object_patterns = [
    path('<int:building_id>/', ObjectsListCreateAPI.as_view(), name='list'),
    path('<int:object_id>/details/', ObjectsUpdateDeleteDetailsAPI.as_view(), name='object-details'),
]

floor_patterns = [
    path('<int:object_id>/', FloorsListCreateAPI.as_view(), name='list'),
    path('<int:floor_id>/details/', FloorsUpdateDeleteDetailsAPI.as_view(), name='details'),
]

detail_patterns = [
    path('<int:floor_id>/', DetailsListCreateAPI.as_view(), name='list'),
    path('<int:detail_id>/details/', DetailsUpdateDeleteDetailsAPI.as_view(), name='detail'),
]

hard_topology_patterns = [
    path('<int:objects_id>/<str:type_obj>/', TopologyHardListCreateView.as_view(), name='list'),
    path('<int:topology_id>/', TopologyHardUpdateDeleteView.as_view(), name='list'),
]

misc_patterns = [
    # path('image/<str:obj>/<int:obj_id>/update', ImageUpdateView.as_view(), name='image-update'),
    # path('topology/<int:objects_id>/<str:type_obj>/create', TopologyHardListCreateView.as_view(), name='topology-create'),
    # path('stock/employee/', StockEmployeeListView.as_view(), name='stock-ex-employee'),
    # path('secure/team-lead/', SecureTeamLeadListCreateView.as_view(), name='secure-team-lead'),
    # path('secure/team-lead/<int:pk>/', SecureTeamLeadUpdateAPI.as_view(), name='secure-team-lead-update'),
    # path('project/complete/', ProjectsCompleteListCreateView.as_view(), name='complete'),
    # path('project/checked/', ProjectsCheckedListCreateView.as_view(), name='checked'),
]

urlpatterns = [
    path('projects/', include((project_patterns, 'projects'))),
    path('buildings/', include((building_patterns, 'buildings'))),
    path('objects/', include((object_patterns, 'objects'))),
    path('floors/', include((floor_patterns, 'floors'))),
    path('details/', include((detail_patterns, 'details'))),
    path('hard-topology/', include((hard_topology_patterns, 'hard-topology'))),
    path('', include((misc_patterns, 'misc'))),
]
