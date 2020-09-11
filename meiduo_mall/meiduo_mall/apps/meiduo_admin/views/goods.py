from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from datetime import date

from users.models import User
from goods.models import GoodsVisitCount,SKU
from meiduo_admin.serializers.goods import SKUGoodsSerializer
from meiduo_admin.utils import UserPageNum
from rest_framework.viewsets import ModelViewSet


class SKUGoodsView(ModelViewSet):
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
