from pprint import pprint

from flask_restful import Resource
from flask import g, request


from utils.api.base_schema import BaseSchema, ExportSchema

from utils.api.api_utils import abort, param_check, param_query, paginator, soft_delete, real_delete


class BaseService(object):
    """
    核心service 类使用必须是在一个appcontext 和 request context 里面
    每个service 对应一个CONFIG CONFIG 类控制接口的显示状态
    """

    def __init__(self):
        self.db_session = g.db_session
        self.query = None
        # self.config = self.Config(self.config_type)
        self.create_query()

    def create_query(self):
        self.query = None

    def before_post(self, data):
        """

        :param data: schema序列化之后的数据,建议在schema层进行数据转化,在这一层进行数据校验
        :return: data
        """
        return data

    def after_post(self, resource, data):
        """

        :param resource: 创建出来的资源
        :param data: 创建资源需要的数据
        :return: None
        """
        return resource

    def before_review(self, resource, data):
        """

        :param resource: 要审核的资源
        :param data: 审核的驱动状态
        :return: 审核的资源
        """
        return resource

    def after_review(self, resource, data):
        """

        :param resource: 要审核的资源
        :param data: 审核的驱动状态
        :return: 审核的资源
        """
        return resource

    def before_delete(self, data):
        """

        :param data: 这是删除之前的数据
        :return:
        """
        return data

    def after_delete(self, resources, data):
        """

        :param resources: 删除的资源的list
        :param data:
        :return:
        """
        return

    def before_put(self, data):
        """

        :param data: schema 序列化之后的数据
        :return:
        """
        return data

    def after_put(self, resource, data):
        """

        :param resource: 修改的资源
        :param data: 数据
        :return:
        """
        return resource


class MyResource(Resource):

    def __init__(self):
        self.db_session = g.db_session
        if request.method != 'GET':
            self.data = request.get_json()
        self.args = request.args
        super().__init__()


class ListResource(MyResource):
    Schema = BaseSchema  # 利用这个schema 来配置
    ExcelSchema = ExportSchema
    Model = None  # 操作那些资源
    Service = BaseService
    parent_id_field = None  # 父ID字段名
    int_query_field = ()  # 那些是INT类型的查询参数
    like_field = ()  # 模糊搜索参数
    between_field = ()  # 之间查询参数
    in_field = ()  # in 参数
    soft_delete = True
    order_by_field = ()
    not_repeat_field = dict()  # {"style_code":[款号,1001],} 编码 1001 名称1002 2001 不存在

    def __init__(self):
        super().__init__()
        self.query = self.db_session.query(self.Model)
        self.service = self.Service()
        self.input = request.get_json()

    def create_order_by(self):
        """
        sql order_by
        @update: sqlalchemy.exc.CompileError: MSSQL requires an order_by
        when using an OFFSET or a non-simple LIMIT clause
        @date: 2020/04/27
        @return:
        """
        if self.order_by_field != ():
            self.query = self.query.order_by(*self.order_by_field)
        else:
            self.query = self.query.order_by(self.Model.create_time.desc())

    def create_query(self):
        self.query = self.query.filter(self.Model.is_delete == 0)
        param = param_check(request.args, int_type=self.int_query_field)
        if param:
            query_obj = param_query([self.Model], param=param, like_fields=self.like_field,
                                    between_field=self.between_field, in_field=self.in_field)
            self.query = self.query.filter(*query_obj)

        # order_by
        self.create_order_by()

    def get(self, parent_id=None):

        self.create_query()
        # 可以定制化的写query对象
        if self.service.query:
            self.query = self.service.query
        if parent_id:
            self.query = self.query.filter(getattr(self.Model, self.parent_id_field) == parent_id)
        # self.query = cus_query_param(self.Model, self.query)

        schema = self.Schema(many=True)
        if 'excel' in request.args:
            schema = self.ExcelSchema(many=True)
            schema.context = {'file_name': str(self.service) + '.xls'}
            return schema.dump(self.query)
        return paginator(self.query, schema)

    def post(self, parent_id=None):
        schema = self.Schema()
        data = schema.load(request.get_json())
        # if error:
        #     abort(400, **error)
        for field in self.not_repeat_field:
            repeat = self.query.filter(getattr(self.Model, field) == data.get(field),
                                       self.Model.is_delete == 0).first()
            if repeat:
                abort(400, message=self.not_repeat_field[field][0] + "已经存在,请更换",
                      code=self.not_repeat_field[field][1])
        data = self.service.before_post(data)
        resource = self.Model()
        resource.update(data)
        if parent_id:
            setattr(resource, self.parent_id_field, parent_id)
        resource.save(self.db_session)
        resource = self.service.after_post(resource, data)
        schema = self.Schema()
        return schema.dump(resource)

    def put(self, parent_id=None):
        resources = self.query.filter(self.Model.id.in_(request.get_json().get('ids'))).all()
        for resource in resources:
            resource.status = request.get_json().get('status')
            resource.save(self.db_session)
        return

    def delete(self, parent_id=None):
        data = self.input
        with self.db_session.begin():
            for i in data:
                self.service.before_delete(data)
                if self.soft_delete:
                    resources = soft_delete(self.Model, i.get('id'))
                else:
                    resources = real_delete(self.Model, i.get('id'))
                self.service.after_delete(resources, data)


class DetailResource(MyResource):
    Model = None
    Schema = BaseSchema
    Service = BaseService
    not_repeat_field = dict()
    soft_delete = True

    def __init__(self):
        super().__init__()
        self.service = self.Service()
        self.input = request.get_json()

    def get(self, resource_id):
        resource = self.db_session.query(self.Model).filter(self.Model.id == resource_id).first()
        schema = self.Schema()
        return schema.dump(resource)

    def put(self, resource_id):
        resource = self.db_session.query(self.Model).filter(self.Model.id == resource_id).first()
        schema = self.Schema()
        data = schema.load(request.get_json())
        # if error:
        #     abort(400, **error)
        for field in self.not_repeat_field:
            repeat = self.db_session.query(self.Model).filter(getattr(self.Model, field) == data.get(field),
                                                              self.Model.is_delete == 0).first()
            if repeat and resource.id != repeat.id:
                abort(400, message=self.not_repeat_field[field] + "已经存在,请更换")
        data = self.service.before_put(data)
        resource.update(data)
        resource.save(self.db_session)
        resource = self.service.after_put(resource, data)
        schema = self.Schema()
        return schema.dump(resource)

    def delete(self, resource_id):
        with self.db_session.begin():
            self.service.before_delete(resource_id)

            if self.soft_delete:
                resources = soft_delete(self.Model, [resource_id])
            else:
                resources = real_delete(self.Model, [resource_id])

            self.service.after_delete(resources, [resource_id])
