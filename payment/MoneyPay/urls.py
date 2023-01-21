from django.urls import path, include
# path("", views.index, name="ShopHome"),
from rest_framework import routers
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)


urlpatterns = [
    path('', include(router.urls)),

    path('home/', views.index, name="index"),
    path('register/', views.register),
    path('login/', views.login),
    path('transfer/', views.transfer),
    path('signup/', views.signup),
    path('signin/', views.signin),
]

urlpatterns += staticfiles_urlpatterns()


app_name = "MoneyPay"
