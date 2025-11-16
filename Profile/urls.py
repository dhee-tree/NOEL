from . import views
from django.urls import path
from .forms import UpdateProfileForm

urlpatterns = [
    path('home/', views.HomeView.as_view(), name='home'),
    path('update-profile/', views.UpdateProfileView.as_view(form=UpdateProfileForm), name='update_profile'),
    path('wishlist/', views.WishListView.as_view(), name='wishlist'),
    path('wishlist/add/', views.AddWishListView.as_view(), name='add_wishlist'),
    path('wishlist/edit/<uuid:item_id>/', views.EditWishListView.as_view(), name='edit_wishlist'),
    path('wishlist/delete/<uuid:item_id>/', views.DeleteWishListView.as_view(), name='delete_wishlist'),

    # API endpoints
    path('', views.UserProfileAPIView.as_view(), name='user_profile_api'),
]
