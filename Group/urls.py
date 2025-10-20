from . import views
from django.urls import path
from .forms import createGroup

urlpatterns = [
    # API endpoints (accessed via /api/groups/)
    path('', views.GroupListCreateAPIView.as_view(), name='group_api_list_create'),
    path('join/', views.JoinGroupAPIView.as_view(), name='group_api_join'),
    path('<uuid:group_id>/', views.GroupDetailAPIView.as_view(), name='group_api_detail'),
    path('<uuid:group_id>/archive/', views.ArchiveGroupAPIView.as_view(), name='group_api_archive'),
    path('<uuid:group_id>/unarchive/', views.UnarchiveGroupAPIView.as_view(), name='group_api_unarchive'),
    path('<uuid:group_id>/toggle-status/', views.ToggleGroupStatusAPIView.as_view(), name='group_api_toggle_status'),
    
    # Template-based views
    path('home/', views.HomeView.as_view(), name='group_home'),
    path('create/', views.CreateGroupView.as_view(form=createGroup), name='group_create'),
    path('join/', views.JoinGroupView.as_view(), name='group_join'),
    path('invite/<str:group_name>/', views.InviteFriendsView.as_view(), name='group_invite'),
    path('leave/<str:group_name>/', views.LeaveGroupView.as_view(), name='group_leave'),
    path('edit/<str:group_name>/', views.EditGroupView.as_view(), name='group_edit'),
    path('status/<str:group_name>/', views.EditGroupStatusView.as_view(), name='group_status'),
    path('view/<str:group_name>/', views.ViewGroupView.as_view(), name='group_view'),
    path('view/<str:group_name>/wrapped/', views.WrappedView.as_view(), name='group_wrapped'),
    path('view/<str:group_name>/unwrapped/', views.UnwrappedView.as_view(), name='group_unwrapped'),
    path('delete/<str:group_name>', views.DeleteGroupView.as_view(), name='group_delete'),
    # path('view/<str:group_name>/add/', views.AddMemberView.as_view(), name='group_add_member'),
    # path('view/<str:group_name>/remove/', views.RemoveMemberView.as_view(), name='group_remove_member'),
]
