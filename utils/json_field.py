from flask import current_app
from sqlalchemy import func



def json_to_field(json_field, sa_type, keys):
    if current_app.config['DATABASE'] == 'postgres':
        for key in keys:
            json_field = json_field[key]
        return json_field.astext.cast(sa_type)
    if current_app.config['DATABASE'] == 'mssql':
        # print('$.'+'.'.join(keys))
        return func.JSON_VALUE(json_field, '$.'+'.'.join(keys)).cast(sa_type)
