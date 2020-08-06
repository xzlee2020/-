from django.shortcuts import render
from django.views import View
import json
from goods import models
from meiduo_mall.utils.response_code import RETCODE
from django_redis import get_redis_connection
import pickle
import base64
from django import http
from . import constants
# Create your views here.
class CartsSelectAllView(View):
    """全选购物车"""

    def put(self, request):
        # 接收参数
        json_dict = json.loads(request.body.decode())
        selected = json_dict.get('selected', True)
        # 校验参数
        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected有误')
        # 判断用户是否登录
        user = request.user
        if user is not None and user.is_authenticated:
            # 用户已登录，操作redis购物车
            redis_conn = get_redis_connection('carts')
            cart = redis_conn.hgetall('carts_%s' % user.id)
            sku_id_list = cart.keys()
            if selected:
                # 全选
                redis_conn.sadd('selected_%s' % user.id, *sku_id_list)
            else:
                # 取消全选
                redis_conn.srem('selected_%s' % user.id, *sku_id_list)
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '全选购物车成功'})
        else:
            # 用户已登录，操作cookie购物车
            cart = request.COOKIES.get('carts')
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '全选购物车成功'})
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
                for sku_id in cart:
                    cart[sku_id]['selected'] = selected
                cookie_cart = base64.b64encode(pickle.dumps(cart)).decode()
                response.set_cookie('carts', cookie_cart, max_age=constants.CART_COOKIE_EXPIRES)
            return response
class CartsSimpleView(View):
    """商品页面右上角购物车"""

    def get(self, request):
        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 用户已登录，查询Redis购物车
            redis_conn = get_redis_connection('carts')
            redis_cart = redis_conn.hgetall('carts_%s' % user.id)
            cart_selected = redis_conn.smembers('selected_%s' % user.id)
            # 将redis中的两个数据统一格式，跟cookie中的格式一致，方便统一查询
            cart_dict = {}
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in cart_selected
                }
        else:
            # 用户未登录，查询cookie购物车
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}
        # 构造简单购物车JSON数据
        cart_skus = []
        sku_ids = cart_dict.keys()
        skus = models.SKU.objects.filter(id__in=sku_ids)
        for sku in skus:
            cart_skus.append({
                'id':sku.id,
                'name':sku.name,
                'count':cart_dict.get(sku.id).get('count'),
                'default_image_url': sku.default_image_url.url
            })

        # 响应json列表数据
        return http.JsonResponse({'code':RETCODE.OK, 'errmsg':'OK', 'cart_skus':cart_skus})

class CartsView(View):
    '''购物车管理'''
    def delete(self, request):
        """删除购物车"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        # 判断sku_id是否存在
        try:
            models.SKU.objects.get(id=sku_id)
        except models.SKU.DoesNotExist:
            return http.HttpResponseForbidden('商品不存在')
        # 判断用户是否登录
        user = request.user
        if user is not None and user.is_authenticated:
            # 用户未登录，删除redis购物车
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            # 删除键，就等价于删除了整条记录
            pl.hdel('carts_%s' % user.id, sku_id)
            pl.srem('selected_%s' % user.id, sku_id)
            pl.execute()
            # 删除结束后，没有响应的数据，只需要响应状态码即可
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除购物车成功'})
        else:
            # 用户未登录，删除cookie购物车
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}
            # 创建响应对象
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除购物车成功'})
            if sku_id in cart_dict:
                del cart_dict[sku_id]
                # 将字典转成bytes,再将bytes转成base64的bytes,最后将bytes转字符串
                cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
                # 响应结果并将购物车数据写入到cookie
                response.set_cookie('carts', cookie_cart_str, max_age=constants.CARTS_COOKIE_EXPIRES)
            return response
    def put(self,request):
        """修改购物车"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)

        # 判断参数是否齐全
        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断sku_id是否存在
        try:
            sku = models.SKU.objects.get(id=sku_id)
        except models.SKU.DoesNotExist:
            return http.HttpResponseForbidden('商品sku_id不存在')
        # 判断count是否为数字
        try:
            count = int(count)
        except Exception:
            return http.HttpResponseForbidden('参数count有误')
        # 判断selected是否为bool值
        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected有误')

        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 用户已登录，修改redis购物车
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            pl.hset('carts_%s'%user.id,sku_id,count)
            if selected:
                pl.sadd('selected_%s'%user.id,sku_id)
            else:
                pl.srem('selected_%s'%user.id,sku_id)
            pl.execute()
            # 创建响应对象
            cart_sku = {
                'id':sku_id,
                'count':count,
                'selected':selected,
                'name': sku.name,
                'default_image_url': sku.default_image_url.url,
                'price': sku.price,
                'amount': sku.price * count,
            }
            return http.JsonResponse({'code':RETCODE.OK, 'errmsg':'修改购物车成功', 'cart_sku':cart_sku})
        else:
            # 用户未登录，修改cookie购物车
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}
            # 因为接口设计为幂等的，直接覆盖
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            # 将字典转成bytes,再将bytes转成base64的bytes,最后将bytes转字符串
            cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()

            # 创建响应对象
            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
                'amount': sku.price * count,
            }
            response = http.JsonResponse({'code':RETCODE.OK, 'errmsg':'修改购物车成功', 'cart_sku':cart_sku})
            # 响应结果并将购物车数据写入到cookie
            response.set_cookie('carts', cookie_cart_str, max_age=constants.CARTS_COOKIE_EXPIRES)
            return response
    
    def get(self,request):
        '''展示购物车'''
        #获取用户
        user = request.user
        #判断用户是否存在
        if user.is_authenticated:
            #用户未登录，获取redis数据
            #获取redis链接对象
            redis_conn = get_redis_connection('carts')
            #获取商品数据sku_ids:count 集合
            redis_cart = redis_conn.hgetall('carts_%s'%user.id)
            #获取选中数据
            cart_selected = redis_conn.smembers('selected_%s'%user.id)
            #构造返回数据 cart_dict
            cart_dict = {}
            for sku_id,count in redis_cart.items():
                cart_dict[int(sku_id)]={
                    'count':int(count),
                    'selected':sku_id in cart_selected
                }
        else:
            #用户未登录，获取cookie
            #获取cookie
            cart_str = request.COOKIES.get('carts')
            #若cart_str 存在则反序列化cart_dict
            if cart_str:
                #将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}
        #构造购物车渲染数据
        #获取购物车中sku_ids
        sku_ids = cart_dict.keys()
        #获取查询集，skus
        skus = models.SKU.objects.filter(id__in=sku_ids)
        cart_skus = []
        
        #构造cart_skus空列表
        for sku in skus:
            cart_skus.append({
                'id':sku.id,
                'name':sku.name,
                'count': cart_dict.get(sku.id).get('count'),
                'selected': str(cart_dict.get(sku.id).get('selected')),  # 将True，转'True'，方便json解析
                'default_image_url':sku.default_image_url.url,
                'price':str(sku.price), # 从Decimal('10.2')中取出'10.2'，方便json解析
                'amount':str(sku.price * cart_dict.get(sku.id).get('count')),
            })

        context = {
            'cart_skus':cart_skus,
        }

        # 渲染购物车页面
        return render(request, 'cart.html', context)

    def post(self,request):
        '''添加购物车'''
        #接收参数
        json_dict = json.loads(request.body.decode())
        #获取参数
        sku_id = json_dict.get('sku_id')
        count=json_dict.get('count')
        selected=json_dict.get('selected',True)
        #校验参数
        #判断参数是否齐全
        if not all([sku_id,count]):
            return http.HttpResponseForbidden('缺少必传参数')
        #判断count是否为数字
        try:
            count = int(count)
        except Excpetion:
            return http.HttpResponseForbidden('参数count有误')
        #判断sku_id是否存在
        try:
            models.SKU.objects.get(id=sku_id)
        except models.SKU.DoesNotExist:
            return http.HttpResponseForbidden('商品不存在')
        #判断selected 是否为布尔类型
        if selected:
            if not isinstance(selected,bool):
                return http.HttpResponseForbidden('参数selected有误')
        #判断用户是否登录
        user = request.user
        if user.is_authenticated:
            #用户已经登录，操作redis
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            #新增购物车数据
            pl.hset('carts_%s'%user.id,sku_id,count)
            #是否选中
            if selected:
                pl.sadd('selected_%s'%user.id,sku_id)
            else:
                pl.srem('selected_%s'%user.id,sku_id)
            pl.execute()
            #响应结果
            return  http.JsonResponse({'code':RETCODE.OK,'errmsg':'添加购物车成功'})
        else:
            #用户未登录，操作cookie
            #获取cookie的购物车
            cart_str = request.COOKIES.get('carts')
            #如果有数据 反序列化获取cart_dict
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            #没有新建cart_dict
            else: 
                cart_dict = {}
            #判断要加入的商品是否在cart_dict里，有则count累加
            if sku_id in cart_dict:
                origin_count = cart_dict['sku_id']['count']
                count += origin_count
            cart_dict[sku_id]={
                'count':count,
                'selected':selected
                }
            print(cart_dict)
            #将字典序列化成字符串
            cookie_cart_str =base64.b64encode(pickle.dumps(cart_dict)).decode()
            #创建响应对象
            response = http.JsonResponse({'code':RETCODE.OK,'errmsg':'添加购物车成功'})
            #写入cookie
            response.set_cookie('carts', cookie_cart_str, max_age=constants.CART_COOKIE_EXPIRES) 
            #响应结果
            return response
