from django.urls import path
from . import views

urlpatterns = [
  path('', views.index, name='index'),
  path('step1', views.convention_select_programme_create, name='step1'),
  path('step1/<convention_uuid>', views.convention_select_programme_update, name='step1_u'),
  path('step2/<convention_uuid>', views.step2, name='step2'),
  path('step3', views.step3, name='step3'),
  path('step4', views.step4, name='step4'),
  path('step5', views.step5, name='step5'),
  path('step6', views.step6, name='step6'),
  path('step7', views.step7, name='step7'),
  path('step8', views.step8, name='step8'),
  path('stepfin', views.stepfin, name='stepfin'),
]
