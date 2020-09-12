from rest_framework import serializers
from goods.models import SpecificationOption,SPUSpecification


class OptionSerialzier(serializers.ModelSerializer):
    spec=serializers.StringRelatedField(read_only=True)
    spec_id=serializers.IntegerField()
    class Meta:
        model = SpecificationOption
        fields = fields="__all__"

class OptionSpecificationSerializer(serializers.ModelSerializer):
    '''规格序列化器'''
    class Meta:
        model = SPUSpecification
        fields = '__all__'
