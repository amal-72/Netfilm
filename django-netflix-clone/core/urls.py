from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('profiles/', views.profile_selection, name='profile_selection'),
    path('profiles/create/', views.create_profile, name='create_profile'),
    path('profiles/edit/<int:profile_id>/', views.edit_profile, name='edit_profile'),
    path('profiles/delete/<int:profile_id>/', views.delete_profile, name='delete_profile'),
    path('profiles/select/<int:profile_id>/', views.select_profile, name='select_profile'),
    path('profiles/update-image/<int:profile_id>/', views.update_profile_image, name='update_profile_image'),
    path('movie/<str:pk>/', views.movie, name='movie'),
    path('genre/', views.all_genres, name='all_genres'),
    path('genre/<str:pk>/', views.genre, name='genre'),
    path('search/', views.search, name='search'),
    path('my-list/', views.my_list, name='my-list'),
    path('add-to-list/', views.add_to_list, name='add-to-list'),
    path('remove-from-list/', views.remove_from_list, name='remove-from-list'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout, name='logout'),
]