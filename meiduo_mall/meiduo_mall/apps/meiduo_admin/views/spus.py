from rest_framework.viewsets import ModelViewSet
from meiduo_admin.utils import UserPageNum
from meiduo_admin.serializers.spus import SPUGoodsSerializer,SPUBrandsSerializer,CategorysSerializer
from meiduo_admin.serializers.skus import SKUGoodsSerializer
from goods.models import SPU,Brand,GoodsCategory,SKU
from rest_framework.response import Response






class SPUGoodsView(ModelViewSet):
    '''SPU表的增删改查'''
    #指定序列化器
    serializer_class = SPUGoodsSerializer
    queryset = SPU.objects.all()
    pagination_class = UserPageNum

    

    def brand(self,request):
        data = Brand.objects.all()
        ser = SPUBrandsSerializer(data,many=True)
        return Response(ser.data)

    def channel(self,request):
        data = GoodsCategory.objects.filter(parent=None)
        ser = CategorysSerializer(data,many=True)
        return Response(ser.data)

    def channels(self,request,pk):
        data = GoodsCategory.objects.filter(parent_id=pk)
        ser=CategorysSerializer(data,many=True)
        return Response(ser.data)

    def image(self,request):
        """
            保存图片
        :param request:
        :return:
        """
        # 1、获取图片数据
        data = request.FILES.get('image')
        # 验证图片数据
        if data is None:
            return Response(status=500)

        # 2、建立fastDFS连接对象
        client = Fdfs_client(settings.FASTDFS_PATH)

        # 3、上传图片
        res = client.upload_by_buffer(data.read())

        # 4、判断上传状态
        if res['Status'] != 'Upload successed.':
            return Response({'error': '上传失败'}, status=501)

        # 5、获取上传的图片路径
        image_url = res['Remote file_id']

        # 6、结果返回
        return Response(
            {
                'img_url': settings.FDFS_URL+image_url
            },

            status=201
        )
class SKUGoodsView(ModelViewSet):
    serializer_class = SKUGoodsSerializer
    pagination_class = UserPageNum
    def get_queryset(self):
        keyword=self.request.query_params.get('keyword')
        if keyword == '' or keyword is None:
            return SKU.objects.all()

        else:
            return SKU.objects.filter(name=keyword)
