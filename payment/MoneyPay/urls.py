from django.urls import path, include
# path("", views.index, name="ShopHome"),
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

urlpatterns = [
    # path("", views.index, name="index"),
    path('', include(router.urls)),

    path('register/', views.register),
    path('login/', views.login),
    path('transfer/', views.transfer),

]

app_name = "MoneyPay"
