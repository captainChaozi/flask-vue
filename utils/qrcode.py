import os

import qrcode
from PIL import Image

from config import static_dir


def make_qrcode(text):
    qr = qrcode.QRCode(version=10,
                       error_correction=qrcode.constants.ERROR_CORRECT_H,
                       box_size=8, border=4)
    qr.add_data(text)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")


def add_image_to_center(back_image, logo_image):
    qrcode_size = back_image.size[0]
    # 创建一个qrcode大小的背景，用于解决黑色二维码粘贴彩色logo显示为黑白的问题。
    qr_back = Image.new('RGBA', back_image.size, 'white')
    qr_back.paste(back_image)
    logo_background_size = int(qrcode_size / 4)
    # 创建一个尺寸为二维码1/4的白底logo背景
    logo_background_image = Image.new('RGBA', (logo_background_size, logo_background_size), 'white')
    # logo与其白底背景设置背景尺寸1/20的留白
    logo_offset = int(logo_background_size / 20)
    logo_size = int(logo_background_size - logo_offset * 2)
    # 将 logo 缩放至适当尺寸
    resized_logo = logo_image.resize((logo_size, logo_size))
    # 将logo添加到白色背景
    logo_background_image.paste(resized_logo, box=(logo_offset, logo_offset))
    # 将白色背景添加到二维码图片
    logo_background_offset = int((qrcode_size - logo_background_size) / 2)
    qr_back.paste(logo_background_image, box=(logo_background_offset, logo_background_offset))
    return qr_back


def create_qr(text, jpg):
    # text_for_qrcode = text
    # logo_image_file = r'avatar.jpg'
    with Image.open(jpg) as logo_image:
        qr_code = make_qrcode(text)
        qr_code_with_logo = add_image_to_center(qr_code, logo_image)
        # return qr_code_with_logo
        file_path = os.path.join(static_dir, text + '.png')
        qr_code_with_logo.save(file_path)
    return file_path
