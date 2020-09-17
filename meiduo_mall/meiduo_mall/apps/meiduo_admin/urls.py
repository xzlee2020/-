from django.conf.urls import url
from django.contrib import admin
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import DefaultRouter
from .views import spus,statistical,users,specs,options,skus,orders,permissions,images
#from .views import statistical,users,specs,images,orders,permissions

urlpatterns =[
    #登录
    url(r'^authorizations/$', obtain_jwt_token),
    #-----数据统计---------------------
    #用户总数统计
    url(r'^statistical/total_count/$',statistical.UserTotalCountView.as_view()),
    #日增用户统计
    url(r'^statistical/day_increment/$',statistical.UserDayCountView.as_view()),
    #日活跃用户统计
    url(r'^statistical/day_active/$',statistical.UserActiveCountView.as_view()),
    #日下单用户统计
    url(r'^statistical/day_orders/$',statistical.UserOrderCountView.as_view()),
    #月增用户统计
    url(r'^statistical/month_increment/$',statistical.UserMonthCountView.as_view()),
    #日分类商品访问量
    url(r'^statistical/goods_day_views/$',statistical.GoodsDayView.as_view()),
    #----------------用户管理---------------
    #查询用户
    url(r'^users/$',users.UserView.as_view()),
    #-----------------商品管理-----------
    #规格路由表
    url(r'^goods/simple/$', specs.SpecsView.as_view({'get': 'simple'})),
    #规格选项表管    /meiduo_admin/goods/specs/simple/
    url(r'^goods/specs/simple/$', options.OptionSimple.as_view()),

    #--------------SKU-----------------------
    #SKU 获取三级分类信息
    url(r'^skus/categories/$', skus.SKUCategorieView.as_view()),
    #SKU 获取SPU表名称
    url(r'^goods/simple/$', skus.SPUSimpleView.as_view()),
    #SKU 获取SPU商品规格信息
    url(r'^goods/(?P<pk>\d+)/specs/$', skus.SPUSpecView.as_view()),
    #SPU品牌信息
    url(r'^goods/brands/simple/$',spus.SPUGoodsView.as_view({'get':'brand'})),
    #获取一级分类信息
    url(r'^goods/channel/categories/$',spus.SPUGoodsView.as_view({'get':'channel'})),
    #获取二三级分类
    url(r'^goods/channel/categories/(?P<pk>\d+)/$',spus.SPUGoodsView.as_view({'get':'channels'})),


    #----------系统管理-----------------
    #获取权限类型
    url(r'^permission/content_types/$',permissions.PermissionView.as_view({'get':'content_types'})),
    #获取权限表数据
    url(r'^permission/simple/$',permissions.GroupView.as_view({'get':'simple'})),
    #获取管理员信息数据
    url(r'^permission/groups/simple/$',permissions.AdminView.as_view({'get':'simple'})),
    #图片路由
    url(r'^skus/simple/$', images.ImageView.as_view({'get': 'simple'})),
#    url(r'^skus/images/$',images.ImagesView.as_view()),
]


#------规格表路由-------
router = DefaultRouter()
router.register('goods/specs',specs.SpecsView,base_name='specs')
urlpatterns += router.urls

#-----SPU-------
router = DefaultRouter()
router.register('goods', spus.SPUGoodsView, base_name='spus')
#router.register('goods/specs',specs.SpecsView,base_name='specs')
urlpatterns += router.urls

#图片路由
router = DefaultRouter()
router.register('skus/images',images.ImageView,base_name='images')
urlpatterns += router.urls

#------规格表路由-------
#router = DefaultRouter()
#router.register('goods/specs',specs.SpecsView,base_name='specs')
#urlpatterns += router.urls

#  /meiduo_admin/specs/options/
#------规格选项表路由----------
router = DefaultRouter()
router.register('specs/options',options.OptionsView,base_name='options')
urlpatterns += router.urls

#------SKU路由表-------------
router = DefaultRouter()
router.register('skus',skus.SKUGoodsView,base_name='skus')
urlpatterns += router.urls



#------订单路由--------------
router = DefaultRouter()
router.register('orders',orders.OrdersView,base_name='orders')
urlpatterns += router.urls

#-----权限路由--------------
router = DefaultRouter()
router.register('permission/perms',permissions.PermissionView,base_name='permissions')
urlpatterns += router.urls
#print(urlpatterns)
#-----用户组路由-------
router = DefaultRouter()
router.register('permission/groups',permissions.GroupView,base_name='groups')
urlpatterns += router.urls

#-----管理员路由------
router = DefaultRouter()
router.register('permission/admins',permissions.AdminView,base_name='admin')
urlpatterns += router.urls

