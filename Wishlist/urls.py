from django.urls import path
from . import views

urlpatterns = [
    path('', views.WishlistListCreateAPIView.as_view(), name='wishlist_list_create'),
    path('<uuid:wishlist_id>/', views.WishlistDetailAPIView.as_view(), name='wishlist_detail'),
    path('<uuid:wishlist_id>/items/', views.WishlistItemListCreateAPIView.as_view(), name='wishlist_items_list_create'),
    path('<uuid:wishlist_id>/items/<uuid:item_id>/', views.WishlistItemDetailAPIView.as_view(), name='wishlist_item_detail'),
]
