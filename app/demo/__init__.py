from .view import DemoListView, DemoItemListView


def demo_register(api):
    api.add_resource(DemoListView, '/demo')
    api.add_resource(DemoItemListView,'/demo/<string:parent_id>/item')