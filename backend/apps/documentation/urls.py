from django.urls import path
from . import views

app_name = 'documentation'

urlpatterns = [
    path('', views.documentation_index, name='index'),
    path('status/', views.documentation_access_status, name='access_status'),
    path('<path:path>', views.DocumentationView.as_view(), name='file'),
]
