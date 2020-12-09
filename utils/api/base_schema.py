import os
import random
import time
from urllib.parse import quote
import pandas as pd
from config import basedir
from flask import send_file, make_response
from marshmallow import Schema, fields, post_dump

from utils.api.api_utils import check_details


class BaseSchema(Schema):
    id = fields.String(validate=check_details)
    extend = fields.Function(lambda obj: obj.extend, allow_none=True)
    create_time = fields.DateTime(format='%Y-%m-%d %H:%M:%S', dump_only=True)
    user_id = fields.String(allow_none=True)
    group_id = fields.String(allow_none=True)
    tenant_id = fields.String(allow_none=True)
    create_user = fields.String(allow_none=True)
    create_group = fields.String(allow_none=True)
    modify_time = fields.DateTime(format='%Y-%m-%d %H:%M:%S', dump_only=True)

    # @pre_load()
    # def cus_process(self, in_data, **kwargs):
    #     cus = in_data.get('cus')
    #     if not cus:
    #         cus = dict()
    #     for k, v in in_data.items():
    #         if 'cus.' in k:
    #             cus[k.split('.')[1]] = v
    #     in_data['cus'] = cus
    #     return in_data
    # # 为了把cus里面的数据dump出去
    # @post_dump
    # def cus_dump(self,data):
    #     cus = data.get('cus')
    #     if cus:
    #         for k,v in cus.items():
    #             data['cus.'+k] = v
    #     return data
    #
    #


class ExportSchema(Schema):
    class Meta:
        ordered = True

    @post_dump(pass_many=True)
    def data_excel(self, data, many):
        data_frame = pd.DataFrame.from_records(data=data)

        time_str = str(time.time())
        random_str = str(random.randint(1, 10000))
        file_name = time_str + random_str + '.xls'

        file_path = os.path.join(basedir, file_name)
        data_frame.to_excel(excel_writer=file_path, index=False)
        response = make_response(send_file(file_path))
        basename = os.path.basename(self.context['file_name'])
        response.headers["Content-Disposition"] = \
            "attachment;" \
            "filename*=UTF-8''{utf_filename}".format(
                utf_filename=quote(basename.encode('utf-8'))
            )
        os.remove(file_path)

        return response
