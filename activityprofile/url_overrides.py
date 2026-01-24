from django.urls import path

from juntagrico import views as juntagrico

from activityprofile.forms import AreaProfileDescriptionForm

urlpatterns = [
    path('my/area/<int:area_id>/', juntagrico.show_area,
         {'form_class': AreaProfileDescriptionForm}),
]
