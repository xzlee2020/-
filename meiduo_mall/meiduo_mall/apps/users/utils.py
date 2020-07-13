from django.contrib.auth.backends import ModelBackend
import re
from .models import User

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
        '''       
        print('user',user)
        if user and user.check_password(password):
            return user
        '''
        user = User.objects.get(username=user.username,password=password)
        if user:
            return user
        else:
            return None
        
