from django.urls import path
from .views import GenerateMockupView, TaskStatusView, MockupListView

urlpatterns = [
    path('generate/', GenerateMockupView.as_view(), name='generate_mockup'),
    path('tasks/<uuid:task_id>/', TaskStatusView.as_view(), name='task_status'),
    path('', MockupListView.as_view(), name='mockup_list'),
]
