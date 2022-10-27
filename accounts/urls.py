from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.index, name="index"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.signin, name="login"),
    path("logout/", views.signout, name="logout"),
    path("<int:pk>/", views.detail, name="detail"),
    path("<int:pk>/follow/", views.follow, name="follow"),
    path("update/", views.update, name="update"),
]
