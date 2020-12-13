from marshmallow import fields,schema
from app.demo.model import Demo, DemoItem
from utils import abort,Schema


class DemoItemSchema(Schema):

    class Meta:
        model = DemoItem


class DemoSchema(Schema):
    items = fields.Nested(DemoItemSchema,many=True)
    hello = fields.Integer()
    num = fields.Number()


    class Meta:
        model = Demo
