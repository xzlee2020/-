from django.conf.urls import url
from django.contrib import admin
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import DefaultRouter
#from .views import statistical,users,specs,images,orders,permissions

urlpatterns =[
    #登录
    url(r'^authorizations/$', obtain_jwt_token),
    #-----数据统计---------------------
]

