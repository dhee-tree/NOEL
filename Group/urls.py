from . import views
from django.urls import path
from .forms import createGroup

urlpatterns = [
    path('home/', views.HomeView.as_view(), name='group_home'),
    path('create/', views.CreateGroupView.as_view(form=createGroup), name='group_create'),
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
