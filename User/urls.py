from django.urls import path
from .views import *

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)


urlpatterns = [

    path('create', CustomUserCreateView.as_view({'post': 'create', 'get': 'list'}), name='user_create'),
    path('update/<int:pk>/', UserPermissionsView.as_view(), name='user-permissions'),

    path('profile/', UserProfileEmployeeView.as_view(), name='user_profile'),
    path('profile-t/', UserProfileTeamLeadView.as_view(), name='user_profile_t'),
    path('project-task/', UserTaskProjectView.as_view(), name='user_project_task'),

    path('teams-user/', UserListRoleView.as_view(), name='teams_user'),
    path('teams-list/', TeamsAPIList.as_view(), name='teams_list'),
    path('teams-list/<int:pk>', TeamsAPIEmployeeUpdate.as_view(), name='teams_d_update'),
    path('teams-list/create', TeamsAPIList.as_view(), name='teams_create'),


    path('rating/', RatingListView.as_view(), name='rating-list'),

    path('users-list/', UserListView.as_view(), name='UserListView'),
    path('users-list/<int:pk>/', UserDetailView.as_view(), name='UserDetailView_detail'),
    path('users-list/task/<int:pk>/', UserDetailTaskView.as_view(), name='UserDetailView_detail_id'),

    path('team-users/', TeamUsersListView.as_view(), name='TeamUsersView'),

    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
