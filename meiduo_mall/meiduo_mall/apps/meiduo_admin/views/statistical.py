from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from datetime import date
from users.models import User
from goods.models import GoodsVisitCount
from meiduo_admin.serializers.statistical import GoodsSerializer
class UserTotalCountView(APIView):
    '''用户总量统计'''

    #指定管理员权限
    permissions_class = [IsAdminUser]
    
    def get(self,request):
        #获取当前日期
        now_date = date.today()
        #获取用户总量
        count = User.objects.all().count()
        return Response({
            'count':count,
            'date':now_date
        })

class UserDayCountView(APIView):
    '''日增用户统计'''
    
    #指定管理员权限
    permissions_class = [IsAdminUser]

    def get(self,request):
        #获取当前日期
        now_date = date.today()
        #获取当日注册用户量
        count = User.objects.filter(date_joined__gte=now_date).count()
        return Response({
            'count':count,
            'date':now_date
        })

class UserActiveCountView(APIView):
    '''日活跃用户量'''
    #指定管理员权限
    permissions_class = [IsAdminUser]

    def get(self,request):
        #获取当前日期
        now_date = date.today()
        #获取当前登录用户数量，字段last_login
        count = User.objects.filter(last_login__gte=now_date).count()
        return Response({
            'count':count,
            'date':now_date
        })
class UserOrderCountView(APIView):
    '''日下单用户量'''

    #指定管理员权限
    permission_classes = [IsAdminUser]
    def get(self,request):
        #获取当前日期
        now_date = date.today()
        #获取当日下单用户数量orders__create_time
        count = User.objects.filter(orders__create_time__gte=now_date).count()
        return Response({
            'count':count,
            'date':now_date
        })


class UserMonthCountView(APIView):
    '''月内日增用户统计'''
    #指定管理员权限
    permission_classes = [IsAdminUser]

    def get(self,request):
        #获取当前日期
        now_date = date.today()
        #获取一个月前日期
        start_date = now_date - timedelta(29)
        #创建空列表保存每天用户量
        date_list = []
        for i in range(30):
            #循环获取当前日期
            index_date = start_date + timedelta(days=i)
            #循环获取次日日期
            cur_date = start_date + timedelta(days=i+1)
            #查询条件是大于当前日期index_date，小于明天日期的用户cur_date，得到当天用户量
            count =User.objects.filter(date_joined__gte=index_date,date_joined__lt=cur_date).count()

            date_list.append({
                'count':count,
                'date':index_date
            })
        return Response(date_list)

class GoodsDayView(APIView):
    '''日分类商品访问量'''
    def get (self,request):
        #获取当前日期
        now_date = date.today()
        #获取当天访问的商品分类数量信息，查询集
        data = GoodsVisitCount.objects.filter(date=now_date)
        
        #序列化返回分类数量
        ser = GoodsSerializer(data,many=True)
        return Response(ser.data)

