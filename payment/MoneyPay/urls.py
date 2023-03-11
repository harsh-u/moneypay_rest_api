from django.urls import path, include
# path("", views.index, name="ShopHome"),
from rest_framework import routers
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)


urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.index, name="index"),
    path('home/', views.index, name="index"),


    # api
    path('register/', views.register),
    path('login/', views.login),
    path('transfer/', views.transfer),


    path('signup/', views.signup),
    path('signin/', views.signin),
    path('money_transfer/', views.money_transfer),
    path('send_money/', views.send_money),
    path('user_profile/', views.user_profile),
    path('user_registration/', views.user_registration),
    path('profile/', views.profile),
    path('user_transaction/', views.user_transaction),
    path('logout/', views.logout),
    path('error_page/', views.error_page),
    path('add_money/', views.add_money),
    path('add_to_razorpay/', views.add_to_razorpay),
    path('add_to_razorpay/paymenthandler/', views.paymenthandler, name='paymenthandler'),
    path('pay_route', include(router.urls)),

]

urlpatterns += staticfiles_urlpatterns()


app_name = "MoneyPay"
