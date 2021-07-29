from django.urls import path
from . import views

urlpatterns = [
  path('', views.index, name='index'),
  path('step1', views.select_programme_create, name='step1'),
  path('step1/<convention_uuid>', views.select_programme_update, name='step1_update'),
  path('step2/<convention_uuid>', views.step2, name='step2'),
  path('step3/<convention_uuid>', views.step3, name='step3'),
  path('step4/<convention_uuid>', views.step4, name='step4'),
  path('step5/<convention_uuid>', views.step5, name='step5'),
  path('step6/<convention_uuid>', views.step6, name='step6'),
  path('step7/<convention_uuid>', views.step7, name='step7'),
  path('step8/<convention_uuid>', views.step8, name='step8'),
  path('step9/<convention_uuid>', views.step9, name='step9'),
  path('stepfin/<convention_uuid>', views.stepfin, name='stepfin'),
]
