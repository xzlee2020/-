from meiduo_admin.utils import UserPageNum
from meiduo_admin.serializers.orders import OrderSeriazlier
from orders.models import OrderInfo
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

class OrdersView(ModelViewSet):
    serializer_class = OrderSeriazlier 
    pagination_class = UserPageNum
    queryset = OrderInfo.objects.all()

    @action(methods=['put'],detail=True)
    def status(self,request,pk):
        #获取订单对象
        order = self.get_object()
        #获取要修改的状态值
        status = request.data.get('status')
        #修改订单状态
        order.status = status
        order.save()
        #返回结果
        ser = self.get_serializer(order)
        return Response({
            'order_id':order.order_id,
            'status':status
        })
