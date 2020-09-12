from meiduo_admin.utils import UserPageNum
from meiduo_admin.serializers.permissions import PermissionSerializer,ContentTypeSerialzier
from meiduo_admin.serializers.permissions import GroupSerialzier,AdminSerializer
from django.contrib.auth.models import Permission,ContentType,Group
from users.models import User
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
class PermissionView(ModelViewSet):
    '''权限管理'''
    serializer_class = PermissionSerializer
    queryset = Permission.objects.all()
    pagination_class = UserPageNum
    
    '''获取权限类型数据'''
    def content_types(self,request):
        #查询全选分类
        content = ContentType.objects.all()
        ser = ContentTypeSerialzier(content,many=True)
        return Response(ser.data)

class GroupView(ModelViewSet):
    '''用户组管理'''
    serializer_class = GroupSerialzier
    pagination_class = UserPageNum
    queryset = Group.objects.all()
    
    #获取权限表数据
    def simple(self,request):
        pers = Permission.objects.all()
        ser = PermissionSerializer(pers, many=True) #使用以前定义的全选序列化器
        return Response(ser.data)

class AdminView(ModelViewSet):
    serializer_class = AdminSerializer
    pagination_class = UserPageNum
    queryset = User.objects.filter(is_staff=True)
    #获取分组数据
    def simple(self,request):
        pers = Group.objects.all()
        ser = GroupSerialzier(pers, many=True)
        return Response(ser.data)
