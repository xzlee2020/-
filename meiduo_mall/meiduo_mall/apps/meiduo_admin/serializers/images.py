from rest_framework import serializers
from goods.models import SKUImage,SKU
from django.conf import settings
from requests import Response
from celery_tasks.static_file.tasks import get_detail_html
from fdfs_client.client import Fdfs_client
'''
class ImageSerializer(serializers.ModelSerializer):
      # 返回图片关联的sku的id值
    sku=serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model=SKUImage
        fields=('sku','image','id')
    def create(self,request,*args,**kwargs):
        #创建FastDFS连接对象
        client = Fdfs_client(settings.FASTDFS_PATH)
        #获取前端传递的image文件
        data = request.FILES.get('image')
        #上传图片到fastDFS
        res = client.upload_by_buffer(data.read())
        #判断是否上传成功
        if res['Status']!='Upload successed.':
            return Response(status=403)
        # 获取上传后的路径
        image_url = res['Remote file_id']
        # 获取sku_id
        sku_id = request.data.get('sku')[0]
        # 保存图片
        img = SKUImage.objects.create(sku_id=sku_id, image=image_url)

        # 生成新的详情页页面
        get_detail_html.delay(img.sku_id)
                # 返回结果
        return Response(
            {
                'id': img.id,
                'sku': sku_id,
                'image': img.image
            },
            status=201  # 前端需要接受201状态
        )
    def update(self, request, *args, **kwargs):

        # 创建FastDFS连接对象
        client = Fdfs_client(settings.FASTDFS_PATH)
        # 获取前端传递的image文件
        data = request.FILES.get('image')
        # 上传图片到fastDFS
        res = client.upload_by_buffer(data.read())
        # 判断是否上传成功
        if res['Status'] != 'Upload successed.':
            return Response(status=403)
        # 获取上传后的路径
        image_url = res['Remote file_id']
        # 获取sku_id
        sku_id = request.data.get('sku')[0]
        # 查询图片对象
        img=SKUImage.objects.get(id=kwargs['pk'])
        # 更新图片
        img.image=image_url
        img.save()
        # 生成新的详情页页面
        get_detail_html.delay(img.sku_id)
        # 返回结果
        return Response(
            {
                'id': img.id,
                'sku': sku_id,
                'image': img.image
            },
            status=201  # 前端需要接受201状态码
        )
'''
class ImageSerializer(serializers.ModelSerializer):
    """
        图片序列化器
    """

    class Meta:
        model = SKUImage
        fields = "__all__"

    def create(self, validated_data):
        # 3、建立fastdfs的客户端
        client = Fdfs_client(settings.FASTDFS_PATH)

        # self.context['request'] 获取request对象

        file = self.context['request'].FILES.get('image')
        # 4、上传图片
        res = client.upload_by_buffer(file.read())
        # 5、判断是否上传成功
        if res['Status'] != 'Upload successed.':
            raise serializers.ValidationError({'error': '图片上传失败'})

        # 6、保存图片表
        img = SKUImage.objects.create(sku=validated_data['sku'], image=res['Remote file_id'])

        #异步生成详情页静态页面
        get_detail_html.delay(img.sku_id)

        return img

    def update(self, instance, validated_data):
        # 3、建立fastdfs的客户端
        client = Fdfs_client(settings.FASTDFS_PATH)

        # self.context['request'] 获取request对象

        file = self.context['request'].FILES.get('image')
        # 4、上传图片
        res = client.upload_by_buffer(file.read())
        # 5、判断是否上传成功
        if res['Status'] != 'Upload successed.':
            raise serializers.ValidationError({'error': '图片上传失败'})

        # 6、更新图片表
        instance.image = res['Remote file_id']
        instance.save()

        # 异步生成详情页静态页面
        get_detail_html.delay(instance.sku_id)
        return instance

class SKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ('id','name')
