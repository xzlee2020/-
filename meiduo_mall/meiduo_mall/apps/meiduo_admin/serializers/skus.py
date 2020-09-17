from rest_framework import serializers
from goods.models import SKU,SKUSpecification,GoodsCategory,SPU
from goods.models import SpecificationOption,SPUSpecification
from django.db import transaction
from celery_tasks.static_file.tasks import get_detail_html

class SKUSpecificationSerialzier(serializers.ModelSerializer):
    '''SKU规格表信息序列化器'''
    spec_id = serializers.IntegerField()
    option_id = serializers.IntegerField()
    class Meta:
        model = SKUSpecification
        fields = ('spec_id','option_id')
    
class SKUGoodsSerializer(serializers.ModelSerializer):
    '''SKU获取信息序列化器'''
    
    # spu = serializers.StringRelatedField(read_only=True)
    spu_id = serializers.IntegerField()
    category_id = serializers.IntegerField()
    #category = serializers.StringRelatedField(read_only=True)
    
    sepcs = SKUSpecificationSerialzier(read_only=True,many=True)
    class Meta:
        model = SKU
        fields = "__all__"
        read_only_fields=('spu','category')
    
    def create(self, validated_data):
      # self指的是当前序列化器对象，在self下面有个context属性保存了请求对象
      specs=self.context['request'].data.get('specs')
      
      # specs = validated_data['specs']
      # 因为sku表中没有specs字段，所以在保存的时候需要删除validated_data中specs数据
      #del validated_data['specs']
      with transaction.atomic():
        # 开启事务
        sid = transaction.savepoint()
        try:
          # 1、保存sku表
          sku = SKU.objects.create(**validated_data)
          # 2、保存SKU具体规格
          for spec in specs:
            SKUSpecification.objects.create(sku=sku, spec_id=spec['spec_id'], option_id=spec['option_id'])
        except:
          # 捕获异常，说明数据库操作失败，进行回滚
          transaction.savepoint_rollback(sid)
          return serializers.ValidationError('数据库错误')
        else:
          # 没有捕获异常，数据库操作成功，进行提交
          transaction.savepoint_commit(sid)
          # 执行异步任务生成新的静态页面
          get_detail_html.delay(sku.id)
          return sku
    def update(self, instance, validated_data):
        # 获取规格信息
        specs = self.context['request'].data.get('specs')
        # 因为sku表中没有specs字段，所以在保存的时候需要删除validated_data中specs数据
        del validated_data['specs']

        with transaction.atomic():
            # 开启事务
            sid = transaction.savepoint()
            try:
                # 1、更新sku表
                SKU.objects.filter(id=instance.id).update(**validated_data)

                # 2、更新SKU具体规格表
                for spec in specs:
                    SKUSpecification.objects.create(sku=instance, spec_id=spec['spec_id'], option_id=spec['option_id'])
            except:
                # 捕获异常，说明数据库操作失败，进行回滚
                transaction.savepoint_rollback(sid)
                return serializers.ValidationError('数据库错误')
            else:
                # 没有捕获异常，数据库操作成功，进行提交
                transaction.savepoint_commit(sid)
                # 执行异步任务生成新的静态页面
                get_detail_html.delay(instance.id)
                return instance
class SKUCategorieSerializer(serializers.ModelSerializer):
    '''获取三级商品序列化器'''
    class Meta:
        model = GoodsCategory
        fields = "__all__"

class SPUSimpleSerializer(serializers.ModelSerializer):
    '''获取SPU表名称数据'''
    class Meta:
        model = SPU
        fields = ('id','name')
class SPUOptineSerializer(serializers.ModelSerializer):
    """
      规格选项序列化器
    """
    class Meta:
        model = SpecificationOption
        fields=('id','value')


class SPUSpecSerialzier(serializers.ModelSerializer):
    '''SPU规格序列化器'''
    # 关联序列化返回SPU表数据
    spu = serializers.StringRelatedField(read_only=True)
    spu_id = serializers.IntegerField(read_only=True)
    # 关联序列化返回 规格选项信息
    options = SPUOptineSerializer(read_only=True,many=True) # 使用规格选项序列化器
    class Meta:
        model = SPUSpecification
        fields = '__all__'

