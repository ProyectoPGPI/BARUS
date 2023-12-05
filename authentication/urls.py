from django.urls import include, path

from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('logout-view', logout_view),
    path('logout/', LogoutView.as_view()),
]