
from rest_framework import serializers
from goods.models import SKU,SKUSpecification

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
