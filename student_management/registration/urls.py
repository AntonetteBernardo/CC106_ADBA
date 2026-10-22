from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_registration, name='student_registration'),
    path('success/', views.registration_success, name='registration_success'),
    path(
        'Home/Registration/',
        views.student_registration,
        name='registration',
    ),
]