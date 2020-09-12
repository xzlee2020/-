from rest_framework.viewsets import ModelViewSet
from goods.models import SpecificationOption,SPUSpecification
from meiduo_admin.serializers.options import OptionSerialzier,OptionSpecificationSerializer
from meiduo_admin.utils import UserPageNum
from rest_framework.generics import ListAPIView


class OptionsView(ModelViewSet):
    '''规格选项表的增删改查'''

    serializer_class = OptionSerialzier
    pagination_class = UserPageNum
    queryset = SpecificationOption.objects.all()

class OptionSimple(ListAPIView):
    '''获取规格信息'''
    serializer_class = OptionSpecificationSerializer
    queryset = SPUSpecification.objects.all()
