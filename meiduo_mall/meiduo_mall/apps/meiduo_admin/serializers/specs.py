from rest_framework import serializers
from goods.models import SPUSpecification,GoodsCategory
from goods.models import SPU,SpecificationOption






class SPUSpecificationSerializer(serializers.ModelSerializer):
    '''规格序列化器'''
    spu = serializers.StringRelatedField(read_only=True)
    spu_id = serializers.IntegerField()
    class Meta:
        model = SPUSpecification
        fields = '__all__'

class SPUSerializer(serializers.ModelSerializer):
    """
        SPU序列化器
    """
    class Meta:
        model = SPU
        fields = ('id', 'name')

class SKUCategorieSerializer(serializers.ModelSerializer):
    '''获取三级商品序列化器'''
    class Meta:
        model = GoodsCategory
        fields = "__all__"

class SPUSimpleSerializer(serializers.ModelSerializer):
    '''获取SPU表名称数据'''
    class Meta:
        model = SPU
        fields = ('id','name')
class SPUOptineSerializer(serializers.ModelSerializer):
    """
      规格选项序列化器
    """
    class Meta:
        model = SpecificationOption
        fields=('id','value')


class SPUSpecSerialzier(serializers.ModelSerializer):
    '''SPU规格序列化器'''
    # 关联序列化返回SPU表数据
    spu = serializers.StringRelatedField(read_only=True)
    spu_id = serializers.IntegerField(read_only=True)
    # 关联序列化返回 规格选项信息
    options = SPUOptineSerializer(read_only=True,many=True) # 使用规格选项序列化器
    class Meta:
        model = SPUSpecification
        fields = '__all__'
