from django.shortcuts import render
from verifications.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django import http
from . import constants
from django.views import View
# Create your views here.

class ImageCodeView(View):
    '''图形验证码'''
    def get(self,request,uuid):
        #生成图片验证码
        text,image = captcha.generate_captcha()

        #保存图片验证码
        redis_conn = get_redis_connection('verify_code')
        redis_conn.setex('img_%s' % uuid,constants.IMAGE_CODE_REDIS_EXPIRES, text)
        #响应图片
        return http.HttpResponse(image,content_type='image/jpg')
