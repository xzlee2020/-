from django.shortcuts import render
from django.views import View
from django import http
#from meiduo_mall.utils.login import LoginRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from users.models import Address
from django_redis import get_redis_connection
from goods.models import SKU,SPU
import json
from meiduo_mall.utils.response_code import RETCODE
from .models import OrderInfo, OrderGoods
from datetime import datetime
from django.utils import timezone
from django.db import transaction
from django.core.paginator import Paginator
from meiduo_mall.utils.views import LoginRequiredJSONMixin
from decimal import Decimal
# Create your views here.

class UserOrderInfoView(LoginRequiredMixin, View):
    '''我的订单'''
    def get(self, request, page_num):
        """提供我的订单页面"""
        user = request.user
        # 查询订单
        orders = user.orderinfo_set.all().order_by("-create_time")
        # 遍历所有订单
        for order in orders:
            # 绑定订单状态
            order.status_name = OrderInfo.ORDER_STATUS_CHOICES[order.status-1][1]
            # 绑定支付方式
            order.pay_method_name = OrderInfo.PAY_METHOD_CHOICES[order.pay_method-1][1]
            order.sku_list = []
            # 查询订单商品
            order_goods = order.skus.all()
            # 遍历订单商品
            for order_good in order_goods:
                sku = order_good.sku
                sku.count = order_good.count
                sku.amount = sku.price * sku.count
                order.sku_list.append(sku)

        # 分页
        page_num = int(page_num)
        try:
            paginator = Paginator(orders, 5)
            page_orders = paginator.page(page_num)
            total_page = paginator.num_pages
        except EmptyPage:
            return http.HttpResponseNotFound('订单不存在')

        context = {
            "page_orders": page_orders,
            'total_page': total_page,
            'page_num': page_num,
        }
        return render(request, "user_center_order.html", context)

class OrderSuccessView(LoginRequiredMixin, View):
    """提交订单成功"""

    def get(self, request):
        order_id = request.GET.get('order_id')
        payment_amount = request.GET.get('payment_amount')
        pay_method = request.GET.get('pay_method')

        context = {
            'order_id':order_id,
            'payment_amount':payment_amount,
            'pay_method':pay_method
        }
        return render(request, 'order_success.html', context)
class OrderCommitView(LoginRequiredJSONMixin, View):
    '''提交订单'''
    def post(self,request):
        '''保存订单信息和订单商品信息'''
        '''获取要保存的信息'''
        #接收参数
        json_dict = json.loads(request.body.decode())
        #获取参数
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')
        #校验参数
        if not all([address_id,pay_method]):
            return http.HttpResponseForbidden('缺少必传参数')
        try:
            address= Address.objects.get(id=address_id)
        except Exception:
            return http.HttpResponseForbidden('参数address_id错误')
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'],OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.HttpResponseForbidden('参数pay_method错误')
        #获取用户
        user =request.user
        '''保存订单信息'''
        #生成订单号
        order_id = timezone.localtime().strftime('%Y%m%d%H%M%S')+('%09d' %user.id)
        
        '''保存订单信息'''
        order = OrderInfo.objects.create(
            order_id=order_id,
            user=user,
            address=address,
            total_count=0,
            total_amount=Decimal('0'),
            freight=Decimal('10.00'),
            pay_method=pay_method,
            status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY'] else
            OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        ) 
        '''保存订单商品信息'''
        # 从redis读取购物车中被勾选的商品信息
        redis_conn = get_redis_connection('carts')
        redis_cart = redis_conn.hgetall('carts_%s' % user.id)
        selected = redis_conn.smembers('selected_%s' % user.id)
        carts = {}
        for sku_id in selected:
            carts[int(sku_id)] = int(redis_cart[sku_id])
        sku_ids = carts.keys()
        #遍历购物车中被勾选商品信息
        for sku_id in sku_ids:
            # 查询SKU信息
            sku = SKU.objects.get(id=sku_id)
            # 判断SKU库存
            sku_count = carts[sku.id]
            if sku_count > sku.stock:
                return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})

            # SKU减少库存，增加销量
            sku.stock -= sku_count
            sku.sales += sku_count
            sku.save()

            # 修改SPU销量
            spu = SPU.objects.get(id=sku.spu_id) 
            spu.sales += sku_count
            spu.save()

            # 保存订单商品信息 OrderGoods（多）
            OrderGoods.objects.create(
                order=order,
                sku=sku,
                count=sku_count,
                price=sku.price,
            )

            # 保存商品订单中总价和总数量
            order.total_count += sku_count
            order.total_amount += (sku_count * sku.price)

        # 添加邮费和保存订单信息
        order.total_amount += order.freight
        order.save()
        # 清除购物车中已结算的商品
        pl = redis_conn.pipeline()
        pl.hdel('carts_%s' % user.id, *selected)
        pl.srem('selected_%s' % user.id, *selected)
        pl.execute()

        # 响应提交订单结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '下单成功', 'order_id': order.order_id})


class OrderSettlementView(LoginRequiredMixin, View):
    """结算订单"""

    def get(self, request):
        """提供订单结算页面"""
        #获取用户
        user = request.user
        #获取用户住址
        try:
            addresses = Address.objects.filter(user=user,is_deleted=False)
        except Address.DoesNotExist:
            #如果地址为空，渲染模板时会判断，并跳转到地址编辑页面
            addresses = None
        #获取redis里的商品数据和选中数据
        redis_conn = get_redis_connection('carts')
        redis_cart = redis_conn.hgetall('carts_%s' % user.id)
        cart_selected=redis_conn.smembers('selected_%s' % user.id)
        #构成cart ={'sku_id': ,'count':}
        cart = {}
        for sku_id in cart_selected:
            cart[int(sku_id)] = int(redis_cart[sku_id])
        #遍历计算总数量和总价格
        total_count = 0
        total_amount = 0
        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            sku.count= cart[sku.id]
            sku.amount = sku.count*sku.price
            total_count += sku.count
            total_amount += sku.count * sku.price
        #补充运费
        freight = 10

        #构成渲染界面数据
        context = {
            'addresses':addresses,
            'skus':skus,
            'total_count':total_count,
            'total_amount':total_amount,
            'freight':freight,
            'payment_amount':freight+total_amount
        }
        return render(request, 'place_order.html',context)
