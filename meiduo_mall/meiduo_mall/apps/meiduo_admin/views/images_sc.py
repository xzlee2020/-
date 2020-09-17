from rest_framework.viewsets import ModelViewSet
from meiduo_admin.utils import UserPageNum
from goods.models import SKUImage
from meiduo_admin.serializers.images import ImagesSerializer

class ImagesView(ModelViewSet):
    serializer_class = ImagesSerializer
    queryset = SKUImage.objects.all()
    pagination_class = UserPageNum
