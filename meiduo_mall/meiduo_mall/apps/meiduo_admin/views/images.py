from rest_framework.viewsets import ModelViewSet
from meiduo_admin.utils import UserPageNum
from goods.models import SKUImage,SKU
from meiduo_admin.serializers.images import ImageSerializer,SKUSerializer
from rest_framework.response import Response

'''
class ImagesView(ModelViewSet):
    serializer_class = ImageSerializer
    queryset = SKUImage.objects.all()
    pagination_class = UserPageNum

    def simple(self,request):
        data = SKU.objects.all()
        ser = SKUSeriazlier(data,many=True)
        return Response(ser.data)
'''

class ImageView(ModelViewSet):
    # 图片序列化器
    serializer_class = ImageSerializer
    # 图片查询集
    queryset = SKUImage.objects.all()
    # 分页
    pagination_class = UserPageNum

    # 获取sku商品信息
    def simple(self,request):
        data = SKU.objects.all()
        ser = SKUSerializer(data,many=True)
        return Response(ser.data)
