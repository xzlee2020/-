from rest_framework.viewsets import ModelViewSet
from meiduo_admin.serializers.specs import SPUSpecificationSerializer,SPUSerializer
from meiduo_admin.utils import UserPageNum
from goods.models import SPUSpecification,SPU
from rest_framework.response import Response



class SpecsView(ModelViewSet):
    serializer_class = SPUSpecificationSerializer
    pagination_class = UserPageNum
    queryset = SPUSpecification.objects.all()

    def simple(self,request):
        '''
        获取商品SPU
        '''
        spus = SPU.objects.all()
        ser = SPUSerializer(spus, many=True)
        return Response(ser.data)
