# @Time    : 2021/2/2
# @Author  : sunyingqiang
# @Email   : 344670075@qq.com
"""
使用元类和描述符类实现简单的ORM操作
"""
import abc
import numbers


class AutoStorage:
    """描述符类"""
    _counter = 0
    def __init__(self):

        cls = self.__class__
        prefix = cls.__name__
        index = cls._counter
        self.storage_name = '_{}{}'.format(prefix, index)   #给描述的属性重新赋值避免递归调用set属性
        cls._counter += 1

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return getattr(instance, self.storage_name)

    def __set__(self, instance, value):
        setattr(instance, self.storage_name, value)


class Validated(abc.ABC, AutoStorage):
    """属性验证抽象基类"""
    def __set__(self, instance, value):
        value = self.validate(instance, value)
        super(Validated, self).__set__(instance, value)

    @abc.abstractmethod
    def validate(self, instance, value):
        pass


class IntegerField(Validated):
    """自定义数字验证类"""

    def validate(self, instance, value):
        if not isinstance(value, numbers.Integral):
            raise ValueError('value must be int')
        return value


class CharField(Validated):
    """自定义字符串验证类"""
    def __init__(self, max_length):
        self.max_length = max_length
        super(CharField, self).__init__()

    def validate(self, instance, value):
        if not isinstance(value, str):
            raise ValueError('value must be str')
        elif len(value) > self.max_length:
            raise ValueError('value exceeds limit')
        return value


class ModelMetaclass(type):
    """构造类"""
    def __new__(cls, name, bases, attrs):
        mappings = dict()
        for k, v in attrs.items():
            if isinstance(v, AutoStorage):
                mappings[k] = v

        attrs['__mappings__'] = mappings
        attrs['__table__'] = name
        return type.__new__(cls, name, bases, attrs)


class Model(object, metaclass=ModelMetaclass):

    def __init__(self, **kwargs):
        for name, value in kwargs.items():         #获取传入的参数并给其赋值
            setattr(self, name, value)

    def save(self):
        """构造出sql语句"""
        fields = []
        args = []
        for k, v in self.__mappings__.items():
            fields.append(k)
            args.append(getattr(self, k, None))

        args_temp = list()
        for temp in args:
            if isinstance(temp, int):
                args_temp.append(str(temp))
            elif isinstance(temp, str):
                args_temp.append("""'%s'""" % temp)
        sql = 'insert into %s (%s) VALUE (%s)' % (self.__table__, ','.join(fields), ','.join(str(i) for i in args_temp))
        print(sql)


class User(Model):
    uid = IntegerField()
    name = CharField(max_length=20)
    email = CharField(max_length=20)
    password = CharField(max_length=5)


u = User(uid=123, name='xxx', email='xx@qq.com', password='1245')
u.save()

