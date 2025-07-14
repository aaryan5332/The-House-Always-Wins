from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/create-session/', views.create_session, name='create_session'),
    path('api/roll/', views.roll_slots, name='roll_slots'),
    path('api/cash-out/', views.cash_out, name='cash_out'),
    path('api/session/<uuid:session_id>/', views.get_session_status, name='session_status'),
] 