from rest_framework import serializers
from goods.models import SKU,SKUSpecification,GoodsCategory,SPU
from goods.models import SpecificationOption,SPUSpecification

class SKUSpecificationSerialzier(serializers.ModelSerializer):
    '''SKU规格表信息序列化器'''
    spec_id = serializers.IntegerField(read_only=True)
    option_id = serializers.IntegerField(read_only=True)
    class Meta:
        model = SKUSpecification
        fields = ("spec_id","option_id")

class SKUGoodsSerializer(serializers.ModelSerializer):
    '''SKU获取信息序列化器'''
    sepcs = SKUSpecificationSerialzier(read_only=True,many=True)
    spu = serializers.StringRelatedField(read_only=True)
    spu_id = serializers.IntegerField()
    category_id = serializers.IntegerField()
    category = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = SKU
        fields = '__all__'

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

