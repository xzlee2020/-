from django.shortcuts import render, redirect
from django.views import View
import re
from django import http
from users.models import User
from django.urls import reverse
from django.contrib.auth import login,authenticate,logout
from meiduo_mall.utils.response_code import RETCODE
from django.contrib.auth.mixins import LoginRequiredMixin
# Createyour views here.

class UserInfoView(LoginRequiredMixin,View):
    '''用户中心'''
    def get(self,request):

        return render(request,'user_center_info.html')

class LogoutView(View):
    '''用户退出'''
    def get(self,request):
        #清理session
        logout(request)
        #删除cookie中的session
        response = redirect(reverse('contents:index'))
        response.delete_cookie('username')
        return response
class LoginView(View):
    '''用户登录'''
    def get(self,request):
        return render(request,'login.html')


    def post(self,request):
        #接收参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')

        #校验参数
        #判断是否齐全
        if not all([username,password]):
            return http.HttpResponseForbidden('缺少必传参数')
        #判断用户名时5-20个字符串
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入正确的用户名或手机号')
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('密码最少8位，最长20位')
        #认证用户登录
        user = authenticate(username=username, password=password)
        print(user)
        if user is None:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码错误'})
        #状态保持
        login(request,user)
        if remembered != 'on':
            request.session.set_expiry(0)
        else:
            request.session.set_expiry(None) #None表示两周有效期
                                            #实际操作显示浏览会话结束时候
        

	#响应登录结果
        #先取出next
        next = request.GET.get('next')
        if next:
            response = redirect(next)
        else:
            response = redirect(reverse('contents:index'))
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)
        #return redirect(reverse('contents:index'))
        return response
class MobileCountView(View):
    '''判断手机号是否重复'''
    def get(self,request,mobile):
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})

class UsernameCountView(View):
    '''判断用户名是否重复注册'''
    def get(self,request,username):
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


class RegisterView(View):
    """用户注册"""

    def get(self, request):
        """提供用户注册页面"""
        return render(request, 'register.html')

    def post(self, request):
        """实现用户注册业务逻辑"""
        # 接收参数：表单参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')

        # 校验参数：前后端的校验需要分开，避免恶意用户越过前端逻辑发请求，要保证后端的安全，前后端的校验逻辑相同
        # 判断参数是否齐全:all([列表])：会去校验列表中的元素是否为空，只要有一个为空，返回false
        if not all([username, password, password2, mobile, allow]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入5-20个字符的用户名')
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # 判断两次密码是否一致
        if password != password2:
            return http.HttpResponseForbidden('两次输入的密码不一致')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')
        # 判断是否勾选用户协议
        if allow != 'on':
            return http.HttpResponseForbidden('请勾选用户协议')

        #保存数据
        try:
            user = User.objects.create(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', {'register_errmsg':'注册失败'})
        #保存状态
        login(request,user)
        #响应结果
        #return http.HttpResponse('注册成功，重定向到首页')
        #return redirect('contents:index')
        response = redirect(reverse('contents:index'))
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)
        return response
