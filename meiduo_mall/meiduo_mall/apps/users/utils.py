from django.contrib.auth.backends import ModelBackend
import re
from .models import User
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
from . import constants
from itsdangerous import BadData

def check_verify_email_token(token):
    """
    验证token并提取user
    :param token: 用户信息签名后的结果
    :return: user, None
    """
    serializer = Serializer(settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
    try:
        data = serializer.loads(token)
    except BadData:
        return None
    else:
        user_id = data.get('user_id')
        email = data.get('email')
        try:
            user = User.objects.get(id=user_id, email=email)
        except User.DoesNotExist:
            return None
        else:
            return user


def generate_verify_email_url(user):
    '''生成邮箱验证链接'''
    serializer = Serializer(settings.SECRET_KEY,expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
    data = {'user_id':user.id,'email':user.email}
    token = serializer.dumps(data).decode()
    verify_url = settings.EMAIL_VERIFY_URL + '?token=' + token
    return verify_url

def get_user_by_acount(acount):
    try:
        if re.match('^1[3-9]\d{9}$', acount):
            user=User.objects.get(mobile=acount)
        else:
            user = User.objects.get(username=acount)

    except User.DoesNotExist:
        return None
    else:
        return user

class UsernameMobileAuthBackend(ModelBackend):
    '''自定义用户认证后端'''
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_by_acount(username)
               
        #print('user',user)
        if user and user.check_password(password):
            return user
        '''
        user = User.objects.get(username=user.username,password=password)
        if user:
            return user
        else:
            return None
        ''' 
