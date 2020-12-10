import datetime
import logging

from marshmallow import ValidationError
from sqlalchemy import Integer, DateTime, Date, DECIMAL, String
from flask import abort as original_flask_abort
from flask import request, jsonify, g,current_app
from flask_restful import reqparse
from sqlalchemy.orm import aliased
from werkzeug.exceptions import HTTPException
from utils.json_field import json_to_field

logger = logging.getLogger('abort')


def remove_spaces(s):
    s = str(s)
    if not (s.startswith(' ') or s.endswith(' ') or s.startswith('\u3000') or s.endswith('\u3000')):
        return s
    s = s.strip(' ')
    s = s.strip('\u3000')
    return remove_spaces(s)


def reflect_date(value):
    try:
        datetime.datetime.strptime(value, '%Y-%m-%d')
        return Date
    except (ValueError, TypeError):
        return False


def reflect_datetime(value):
    if len(value) == 10:
        try:
            datetime.datetime.strptime(value, '%Y-%m-%d')
            return DateTime
        except (ValueError, TypeError):
            return False
    elif len(value) == 19:
        try:
            datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            return DateTime
        except (ValueError, TypeError):
            return False
    else:
        return False


def reflect_number(value):
    try:
        float(value)
        return DECIMAL(20,5)
    except (ValueError, TypeError):
        return False


def check_param(value, _type):
    if isinstance(_type, Date):
        try:
            value = datetime.datetime.strptime(value, '%Y-%m-%d')
        except (ValueError, TypeError):
            abort(400, message="时间参数不正确")
    elif isinstance(_type, DateTime):
        if len(value) == 10:
            try:
                value = datetime.datetime.strptime(value, '%Y-%m-%d')
            except (ValueError, TypeError):
                abort(400, message="时间参数不正确")
        elif len(value) == 19:
            try:
                value = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                abort(400, message="时间参数不正确")
        else:
            abort(400, message="时间参数不正确")
    elif isinstance(_type, (Integer, DECIMAL)):
        try:
            value = float(value)
        except (ValueError, TypeError):
            abort(400, message="数字参数不正确")
    else:
        value = str(value)
    return value


def cus_cov_param(model, field, sa_type, op, value):
    if op == 'EQ':
        return json_to_field(model.cus, sa_type, [field]) == value
        # return model.cus[field].astext.cast(sa_type) == value
    elif op == 'LIKE':
        return json_to_field(model.cus, sa_type, [field]).ilike("%{}%".format(value))
        # return model.cus[field].astext.cast(sa_type).ilike("%{}%".format(value))
    elif op == 'GT':
        return json_to_field(model.cus, sa_type, [field]) > value

        # return model.cus[field].astext.cast(sa_type) > value
    elif op == 'GTE':
        return json_to_field(model.cus, sa_type, [field]) >= value

        # return model.cus[field].astext.cast(sa_type) >= value
    elif op == 'LT':
        return json_to_field(model.cus, sa_type, [field]) < value
        # return model.cus[field].astext.cast(sa_type) < value
    elif op == 'LTE':
        return json_to_field(model.cus, sa_type, [field]) <= value
        # return model.cus[field].astext.cast(sa_type) <= value
    elif op == 'NEQ':
        return json_to_field(model.cus, sa_type, [field]) != value
        # return model.cus[field].astext.cast(sa_type) != value
    else:
        return None


# 转化参数
def cov_param(field, model, op, value, _type):
    # 判断等于
    value = check_param(value, _type)
    if op == 'EQ':
        return getattr(model, field) == value
    elif op == 'LIKE':
        return getattr(model, field).like("%{}%".format(value))
    elif op == 'GT':
        return getattr(model, field) > value
    elif op == 'GTE':
        return getattr(model, field) >= value
    elif op == 'LT':
        return getattr(model, field) < value
    elif op == 'LTE':
        return getattr(model, field) <= value
    elif op == 'NEQ':
        return getattr(model, field) != value
    else:
        return None


def cus_query_param(model, query):
    # @ 分割
    params = dict()
    columns = model.__table__.columns
    res = []
    for k, v in request.args.items():
        if '@' not in k:
            continue
        field, op = k.split("@")
        if '.' in field:
            fk_obj, fk_obj_field = field.split('.')
            # print(fk_obj,fk_obj)
            if fk_obj == 'cus':
                # 猜测是什么sqlalchemy 类型
                for reflect in (reflect_date, reflect_datetime, reflect_number):
                    sa_type = reflect(v)
                    if sa_type:
                        break
                if not sa_type:
                    sa_type = String
                value = check_param(value=v, _type=sa_type)
                query_str = cus_cov_param(model, fk_obj_field, sa_type, op, value)
            else:
                if not hasattr(model, fk_obj):
                    abort(400, message="该对象没有这个属性")
                fk_model = getattr(model, fk_obj).property.argument()
                alised_model = aliased(fk_model)
                query_str = cov_param(fk_obj_field, fk_model, op, v,
                                      getattr(fk_model.__table__.columns, fk_obj_field).type)
                query = query.outerjoin(alised_model, getattr(model, fk_obj), aliased=True)

        else:
            if field not in columns:
                abort(400, message="该字段不存在")
            # 操作 值 那个model 字段类型
            params[field] = [op, v, model, getattr(columns, field)]
            query_str = cov_param(field, model, op, v, getattr(columns, field).type)
        if query_str is not None:
            res.append(query_str)

    return query.filter(*res)


def param_check(args=(), int_type=()):
    """
    构造参数解析器
    :param args: list 解析那些request.args参数
    :param int_type: 要解析成int的有那些
    :return: dict
    """
    parse = reqparse.RequestParser(bundle_errors=True)
    for arg in args:
        if arg in int_type:
            parse.add_argument(arg, type=int, location='args', store_missing=False)
        else:
            # print(1111111)

            parse.add_argument(arg, type=str, location='args', store_missing=False)
    # print(parse)
    param = parse.parse_args()
    return param


def param_query(models, param=None, like_fields=(), between_field=(), in_field=()):
    param = dict(param)
    param_list = []
    for model in models:
        for k, v in param.items():
            if getattr(model, k, None):
                if k in like_fields:
                    param_list.append(getattr(model, k).ilike('%{}%'.format(remove_spaces(v))))
                elif k in in_field:
                    param_list.append(getattr(model, k).in_(v if isinstance(v, list) else [v]))
                else:
                    param_list.append(getattr(model, k) == v)
        for i in between_field:
            start = i + '_start'
            end = i + '_end'
            if (start in param) and (end in param) and getattr(model, i, None):
                if start.find('time') != -1 and end.find('time') != -1:
                    start = datetime.datetime.strptime(param.get(start), '%Y-%m-%d')
                    end = datetime.datetime.strptime(param.get(end), "%Y-%m-%d") + datetime.timedelta(days=1)
                elif start.find('data') != -1 and end.find('data') != -1:
                    start = datetime.datetime.strptime(param.get(start), '%Y-%m-%d')
                    end = datetime.datetime.strptime(param.get(end), "%Y-%m-%d") + datetime.timedelta(days=1)
                else:
                    start = param.get(start)
                    end = param.get(end)
                param_list.append(getattr(model, i).between(start, end))

    return tuple(param_list)


def paginator(query, schema):
    page = request.args.get('page', 1)
    per_page = request.args.get('per_page', 10)
    pagination = query.paginate(page=int(page), per_page=int(per_page), error_out=False)
    total_number = pagination.total  # 获取总条数
    items = pagination.items  # 获取数据
    result = schema.dump(items)
    return jsonify({
        'data': result,
        'paging': {'page': int(page),
                   'per_page': int(per_page),
                   'total_number': int(total_number)}
    })


def abort(http_status_code, **kwargs):
    """
    来自于flask_restful 只有在flask_restful的框架中才起作用
    :param http_status_code:
    :param kwargs:
    :return:
    """
    try:
        original_flask_abort(http_status_code)
    except HTTPException as e:
        if len(kwargs):
            e.data = kwargs
            current_app.logger.error(kwargs)
        raise


def soft_delete(model, ids):
    db_session = g.db_session
    if not isinstance(ids, list):
        ids = [ids]
    # @update: AttributeError: type object 'Category' has no attribute 'id' @date: 2020/04/27
    ins = db_session.query(model).filter(model.id.in_(ids)).all()
    print(ins)
    for i in ins:
        i.is_delete = 1
        i.save(db_session)
    return None


def real_delete(model, ids):
    db_session = g.db_session
    if not isinstance(ids, list):
        ids = [ids]
    # @update: AttributeError: type object 'Category' has no attribute 'id' @date: 2020/04/27
    db_session.query(model).filter(model.id.in_(ids)).delete(synchronize_session=False)
    return None


# schema校验字符串不能为空字符串
def check_details(details):
    if details == '':
        raise ValidationError('内容不能为空字符串')
