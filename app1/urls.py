from django.urls import path
from . import views
app_name = 'app1'

urlpatterns = [
    path('',views.index,name='index'),
    path('array-api',views.array_api,name='array_api'),
    path('get-array',views.get_array,name='get_array'),
]