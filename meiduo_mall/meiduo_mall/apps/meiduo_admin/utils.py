from django.contrib.auth.backends import ModelBackend
import re
from users.models import User

def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt认证成功返回数据
    """
    return {
        'token': token,
        'id': user.id,
        'username': user.username
    }
class MeiduoModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 判断是否通过vue组件发送请求
        if request is None:
            try:
                user = User.objects.get(username=username, is_staff=1)
            except:
                return None
            # 判断密码
            if user.check_password(password):
                return user

        else:
            # 变量username的值，可以是用户名，也可以是手机号，需要判断，再查询
            try:
                # if re.match(r'^1[3-9]\d{9}$', username):
                #     user = User.objects.get(mobile=username)
                # else:
                #     user = User.objects.get(username=username)
                print('通过前端登陆')
                user = User.objects.get(username=username)
            except:
                # 如果未查到数据，则返回None，用于后续判断
                try:
                    user = User.objects.get(mobile=username)
                except:
                    return None
                    # return None

            # 判断密码
            print('开始判断密码')
            if user.check_password(password):
                return user
            else:
                return None
