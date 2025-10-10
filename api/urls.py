from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"sermons", views.SermonViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    path("auth/register/", views.register_user, name="api_register"),
    path("auth/login/", views.login_user, name="api_login"),
    path("auth/logout/", views.logout_user, name="api_logout"),
]
