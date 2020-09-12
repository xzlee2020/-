from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from datetime import date

from users.models import User
from goods.models import GoodsVisitCount,SKU,GoodsCategory,SPU,SPUSpecification
from meiduo_admin.serializers.skus import SKUGoodsSerializer,SPUSimpleSerializer,SKUCategorieSerializer
from meiduo_admin.serializers.skus import SPUSpecSerialzier
from meiduo_admin.utils import UserPageNum
from rest_framework.viewsets import ModelViewSet


class SKUGoodsView(ModelViewSet):
    '''获取SKU信息'''
    #指定序列化器
    serializer_class = SKUGoodsSerializer
    #指定分页器
    pagination = UserPageNum
    #重写获取查询集
    def get_queryset(self):
        #提取keyword
        keyword = self.request.query_params.get('keyword')
        if keyword == ''or keyword is None:
            return SKU.objects.all()
        else:
            return SKU.objects.filter(name=keyword)

class SKUCategorieView(ListAPIView):
    '''获取三级分类信息'''
    serializer_class = SKUCategorieSerializer
    #定义查询集为三级分类商品
    queryset = GoodsCategory.objects.filter(parent_id__gt=37)

class SPUSimpleView(ListAPIView):
    '''获取spu表名称数据'''
    serializer_class = SPUSimpleSerializer
    queryset = SPU.objects.all()

class SPUSpecView(ListAPIView):
    serializer_class = SPUSpecSerialzier
    
    def get_queryset(self):
        pk = self.kwargs['pk']
        return SPUSpecification.objects.filter(spu_id=pk)

