import re
import six
import sqlalchemy
from flask import request, g
from sqlalchemy import inspect, util, orm
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import object_mapper
from flask_sqlalchemy import abort, Pagination
from sqlalchemy.orm.base import _entity_descriptor

from utils.model.user_info import get_user, get_tenant

_camelcase_re = re.compile(r'([A-Z]+)(?=[a-z0-9])')


def to_str(x, charset='utf8', errors='strict'):
    if x is None or isinstance(x, str):
        return x

    if isinstance(x, bytes):
        return x.decode(charset, errors)

    return str(x)


def iteritems(d):
    return iter(d.items())


def _should_set_tablename(cls):
    for base in cls.__mro__:
        d = base.__dict__

        if '__tablename__' in d or '__table__' in d:
            return False

        for name, obj in iteritems(d):
            if isinstance(obj, declared_attr):
                obj = getattr(cls, name)

            if isinstance(obj, sqlalchemy.Column) and obj.primary_key:
                return True


def camel_to_snake_case(name):
    def _join(match):
        word = match.group()

        if len(word) > 1:
            return ('_%s_%s' % (word[:-1], word[-1])).lower()

        return '_' + word.lower()

    return _camelcase_re.sub(_join, name).lstrip('_')


class Model(six.Iterator):
    #: Query class used by :attr:`query`.
    #: Defaults to :class:`SQLAlchemy.Query`,
    #  which defaults to :class:`BaseQuery`.
    query_class = None

    #: Convenience property to query the database for instances of
    #  this model using the current session.
    #: Equivalent to ``db.session.query(Model)`` unless
    # :attr:`query_class` has been changed.
    query = None

    _cached_tablename = None


    def __repr__(self):
        identity = inspect(self).identity
        # print(identity)
        if identity is None:
            pk = "(transient {0})".format(id(self))
        else:
            pk = ', '.join(to_str(value) for value in identity)
        return '<{0} {1}>'.format(type(self).__name__, pk)

    def delete(self, session):
        with session.begin(subtransactions=True):
            session.delete(self)
            session.flush()

    def save(self, session):
        """Save this object."""
        with session.begin(subtransactions=True):
            session.add(self)
            session.flush()

    def update(self, values):
        """Make the model object behave like a dict."""
        for k, v in six.iteritems(values):
            setattr(self, k, v)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def __contains__(self, key):

        try:
            getattr(self, key)
        except AttributeError:
            return False
        else:
            return True

    def get(self, key, default=None):
        return getattr(self, key, default)

    @property
    def _extra_keys(self):
        """Specifies custom fields

        Subclasses can override this property to return a list
        of custom fields that should be included in their dict
        representation.

        For reference check tests/db/sqlalchemy/test_models.py
        """
        return []

    def __iter__(self):
        columns = list(dict(object_mapper(self).columns).keys())
        columns.extend(self._extra_keys)

        return ModelIterator(self, iter(columns))

    def _as_dict(self):
        """Make the model object behave like a dict.

        Includes attributes from joins.
        """
        local = dict((key, value) for key, value in self)
        # print(local)
        joined = dict([(k, v) for k, v in six.iteritems(self.__dict__)
                       if not k[0] == '_'])
        local.update(joined)
        return local

    def iteritems(self):
        """Make the model object behave like a dict."""
        return six.iteritems(self._as_dict())

    def items(self):
        """Make the model object behave like a dict."""
        return self._as_dict().items()

    def keys(self):
        """Make the model object behave like a dict."""
        return [key for key, value in self.items()]

    def as_dict(self):
        d = {}
        for c in self.__table__.columns:
            d[c.name] = self[c.name]
        return d
    @classmethod
    def field_comments(cls):
        d = dict()
        for c in cls.__table__.columns:
            if c.comment:
                d[c.name] = c.comment
        return d


class ModelIterator(six.Iterator):

    def __init__(self, model, columns):
        self.model = model
        self.i = columns

    def __iter__(self):
        return self

    # In Python 3, __next__() has replaced next().
    def __next__(self):
        n = six.next(self.i)
        # print(n)
        return n, getattr(self.model, n)


def _generative(*assertions):
    """Mark a method as generative, e.g. method-chained."""

    @util.decorator
    def generate(fn, *args, **kw):
        self = args[0]._clone()
        for assertion in assertions:
            assertion(self, fn.__name__)
        fn(self, *args[1:], **kw)
        return self

    return generate


class BaseQuery(orm.Query):
    """SQLAlchemy :class:`~sqlalchemy.orm.query.Query` subclass with convenience methods for querying in a web application.

    This is the default :attr:`~Model.query` object used for models, and exposed as :attr:`~SQLAlchemy.Query`.
    Override the query class for an individual model by subclassing this and setting :attr:`~Model.query_class`.
    """

    def tenant_filter(self):
        try:
            user = g.user
        except AttributeError:
            return self
        res = self
        tenant_id = get_tenant()
        if tenant_id:
            res = res.filter_by(tenant_id=tenant_id)
        p_type = user.get('data_permission_type')
        if p_type == 'self':
            res = res.filter_by(user_id=get_user())
        elif p_type == 'all':
            res = res
        else:
            # print(g.user)
            clauses = [_entity_descriptor(res._joinpoint_zero(), 'group_id').in_(user['group_ids'])]
            res = res.filter(sqlalchemy.sql.and_(*clauses))
        return res

    def get_or_404(self, ident):
        """Like :meth:`get` but aborts with 404 if not found instead of returning ``None``."""

        rv = self.get(ident)
        if rv is None:
            abort(404)
        return rv

    def first_or_404(self):
        """Like :meth:`first` but aborts with 404 if not found instead of returning ``None``."""

        rv = self.first()
        if rv is None:
            abort(404)
        return rv

    def paginate(self, page=None, per_page=None, error_out=True, max_per_page=None):
        """Returns ``per_page`` items from page ``page``.

        If ``page`` or ``per_page`` are ``None``, they will be retrieved from
        the request query. If ``max_per_page`` is specified, ``per_page`` will
        be limited to that value. If there is no request or they aren't in the
        query, they default to 1 and 20 respectively.

        When ``error_out`` is ``True`` (default), the following rules will
        cause a 404 response:

        * No items are found and ``page`` is not 1.
        * ``page`` is less than 1, or ``per_page`` is negative.
        * ``page`` or ``per_page`` are not ints.

        When ``error_out`` is ``False``, ``page`` and ``per_page`` default to
        1 and 20 respectively.

        Returns a :class:`Pagination` object.
        """

        if request:
            if page is None:
                try:
                    page = int(request.args.get('page', 1))
                except (TypeError, ValueError):
                    if error_out:
                        abort(404)

                    page = 1

            if per_page is None:
                try:
                    per_page = int(request.args.get('per_page', 20))
                except (TypeError, ValueError):
                    if error_out:
                        abort(404)

                    per_page = 20
        else:
            if page is None:
                page = 1

            if per_page is None:
                per_page = 20

        if max_per_page is not None:
            per_page = min(per_page, max_per_page)

        if page < 1:
            if error_out:
                abort(404)
            else:
                page = 1

        if per_page < 0:
            if error_out:
                abort(404)
            else:
                per_page = 20
        # res = self

        res = self.tenant_filter()
        items = res.limit(per_page).offset((page - 1) * per_page).all()
        if not items and page != 1 and error_out:
            abort(404)

        # No need to count if we're on the first page and there are fewer
        # items than we expected.
        if page == 1 and len(items) < per_page:
            total = len(items)
        else:
            total = res.order_by(None).count()

        return Pagination(res, page, per_page, total, items)

    def __iter__(self):
        try:
            res = self.tenant_filter()
        except InvalidRequestError:
            res = self
        context = res._compile_context()
        context.statement.use_labels = True
        if res._autoflush and not res._populate_existing:
            res.session._autoflush()
        return res._execute_and_instances(context)
