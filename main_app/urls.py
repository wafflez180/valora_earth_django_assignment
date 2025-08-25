from django.urls import path
from django.conf import settings
from . import views

app_name = 'main_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('estimate/', views.estimate_questionnaire, name='estimate_questionnaire'),
    path('loading-estimate/', views.loading_screen, name='loading_screen'),
    path('estimate-results/<int:inquiry_id>/', views.estimate_results, name='estimate_results'),
    path('api/generate-estimate/<int:inquiry_id>/', views.generate_ai_estimate, name='generate_ai_estimate'),
]

# Only include debug endpoints when DEBUG is True
if settings.DEBUG:
    urlpatterns += [
        path('debug/session/', views.debug_session, name='debug_session'),
    ]
