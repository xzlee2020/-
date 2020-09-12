from orders.models import OrderInfo,SKU,OrderGoods
from rest_framework import serializers

class SKUGoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ('name','default_image_url')


class OrderGoodsSerialziers(serializers.ModelSerializer):
    sku = SKUGoodsSerializer(read_only=True)
    class Meta:
        model = OrderGoods
        fields = ('count','price','sku')


class OrderSeriazlier(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    skus = OrderGoodsSerialziers(many=True,read_only=True)
    class Meta:
        model = OrderInfo 
        fields = '__all__'
