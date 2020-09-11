from rest_framework import serializers
from users.models import User

class UserSerializer(serializers.ModelSerializer):
    '''用户查询，序列化器'''
    class Meta:
        model = User
        fields = ('id','username','mobile','email')

class UserAddSerializer(serializers.ModelSerializer):
    '''增加用户，序列化器'''
    class Meta:
        model = User
        fields = ('id','username','mobile','email','password')

        extra_kwargs = {
            'username':{
                'max_length':20,
                'min_length':5
            },
            'password':{
                'max_length':20,
                'min_length':8,
                'write_only':True #密码只读不返回给前端
            }
        }
    #重写create方法
    def create(self,validated_data):
        #保存用户数据并对密码加密
        user = User.objects.create_user(**validated_data)
        return user

