from . import views
from django.urls import path

urlpatterns = [
    path('home/', views.HomeView.as_view(), name='group_home'),
    path('create/', views.CreateGroupView.as_view(), name='group_create'),
    path('view/<str:group_name>/', views.ViewGroupView.as_view(), name='group_view'),
    path('view/<str:group_name>/wrapped/', views.WrappedView.as_view(), name='group_wrapped'),
    path('view/<str:group_name>/unwrapped/', views.UnwrappedView.as_view(), name='group_unwrapped'),
    # path('view/<str:group_name>/edit/', views.EditGroupView.as_view(), name='group_edit'),
    # path('view/<str:group_name>/delete/', views.DeleteGroupView.as_view(), name='group_delete'),
    # path('view/<str:group_name>/add/', views.AddMemberView.as_view(), name='group_add_member'),
    # path('view/<str:group_name>/remove/', views.RemoveMemberView.as_view(), name='group_remove_member'),
]
