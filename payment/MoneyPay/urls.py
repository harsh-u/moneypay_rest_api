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
    path('user_api/', views.snippet_list),
    path('transfer/', views.transfer),
    path('login/', views.login),

]

app_name = "MoneyPay"
