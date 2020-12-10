from app.demo.model import Demo, DemoItem
from app.demo.schema import DemoSchema, DemoItemSchema
from utils import ListResource

class DemoListView(ListResource):

    Model = Demo
    Schema = DemoSchema

class DemoItemListView(ListResource):

    Model = DemoItem
    Schema = DemoItemSchema
    parent_id_field = 'demo_id'