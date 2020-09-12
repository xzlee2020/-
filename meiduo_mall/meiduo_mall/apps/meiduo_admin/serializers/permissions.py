from django.contrib.auth.models import Permission, ContentType,Group
from users.models import User
from rest_framework import serializers


class PermissionSerializer(serializers.ModelSerializer):
    '''用户权限表序列化器'''
    class Meta:
        model = Permission
        fields = '__all__'


class ContentTypeSerialzier(serializers.ModelSerializer):
    '''权限类型序列化器'''
    class Meta:
        model = ContentType
        fields = ('id','name')

class GroupSerialzier(serializers.ModelSerializer):
    '''用户组权限管理'''
    class Meta:
        model = Group
        fields = '__all__'
'''
class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs ={
            'password':{
                'write_only':True
            }
        }
        #重写父类方法，增加管理员权限属性
        def create(self,validated_data):
            #创建管理员用户
            username = validated_data['username']
            mobile = validated_data['mobile']
            password = validated_data['password']
            print(username,mobile)
            admin = User.objects.create(username=username, password=password,mobile=mobile)
            #添加管理员权限
            admin.is_staff = True
            
            user=admin.save()
            print (user.is_staff)
            return user
        
        def update(self,validated_data):
            admin = super().update(instance,validated_data)
            password = validated_data['password']
            admin.set_password(password)
            admin.save()
            return admin
'''
class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        # 给字段增加额外参数
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    # 父类保存数据库的方法不满足需求，重写方法
    def create(self, validated_data):
        user = super().create(validated_data)
        user.is_staff = True
        # 密码加密set_password
        user.set_password(validated_data['password'])
        user.save()

        return user

    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        # 密码加密set_password
        user.set_password(validated_data['password'])
        user.save()
        return user
