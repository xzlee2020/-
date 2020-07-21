from django.shortcuts import render
from django.views import View
from collections import OrderedDict

from contents.models import ContentCategory
from contents.utils import get_categories

# Create your views here.

class IndexView(View):
    '''首页展示'''
    def get(self,request):
        '''提供首页广告'''
        #查询商品频道和分类
        categories = get_categories()
        #广告数据
        contents = {}
        content_categories = ContentCategory.objects.all()
        for cat in content_categories:
            contents[cat.key]=cat.content_set.filter(status=True).order_by('sequence')
        # 渲染模板的上下文
        context = {
            'categories': categories,
            'contents': contents,
        }
        return render(request,'index.html',context)
