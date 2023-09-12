from django.urls import path

from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('viewurl/<str:pid>/', views.url_details, name='url_details'),
    path('img/<str:pid>/', views.img_details, name='img_details'),

    # path('location/<str:pid>', views.loc_details, name='loc_details'),
]
