from rest_framework import serializers
from goods.models import SKUImage

class ImagesSerializer(serializers.ModelSerializer):
    
    sku_id = serializers.IntegerField()
    class Meta:
        model = SKUImage
        fields = '__all__'
