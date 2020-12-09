from Crypto.Cipher import AES
import base64

from Crypto.Util.Padding import pad


class AesCrypt:
    def __init__(self, model, iv, encode_, key='abcdefghijklmnop'):
        self.encrypt_text = ''
        self.decrypt_text = ''
        self.encode_ = encode_
        self.model = {'ECB': AES.MODE_ECB, 'CBC': AES.MODE_CBC}[model]
        self.key = self.add_16(key)
        if model == 'ECB':
            self.aes = AES.new(self.key, self.model)  # 创建一个aes对象
        elif model == 'CBC':
            self.aes = AES.new(self.key, self.model, iv)  # 创建一个aes对象

        # 这里的密钥长度必须是16、24或32，目前16位的就够用了

    def add_16(self, par):
        par = par.encode(self.encode_)
        while len(par) % 16 != 0:
            par += b'\x00'
        return par

    # 加密
    def aesencrypt(self, text):
        text = pad(text.encode('utf-8'), AES.block_size, style='pkcs7')
        self.encrypt_text = self.aes.encrypt(text)
        return base64.encodebytes(self.encrypt_text).decode().strip()

    # 解密
    def aesdecrypt(self, text):
        text = base64.decodebytes(text.encode(self.encode_))
        self.decrypt_text = self.aes.decrypt(text)
        return self.decrypt_text.decode(self.encode_).rstrip("\x01").\
            rstrip("\x02").rstrip("\x03").rstrip("\x04").rstrip("\x05").\
            rstrip("\x06").rstrip("\x07").rstrip("\x08").rstrip("\x09").\
            rstrip("\x0a").rstrip("\x0b").rstrip("\x0c").rstrip("\x0d").\
            rstrip("\x0e").rstrip("\x0f").rstrip("\x10")

pr = AesCrypt("ECB", "", "utf-8")
des_decrypt = pr.aesdecrypt



if __name__ == '__main__':
    print('明文:', des_decrypt('b7jtFk5XInLAiXUQxnxMHwIjGSSMorpnocdpIqAYMvF3tFMo7+/C5v0ts34ua/FpQ1xovFpPi5VV2oz+uTnsrSW06YiN/Be5Ctvu+12XCg+0Em4hWXlFB2g/zNnNr9cJQ+nR261KWsgesr+O/yk1UFvPgEmoVJX6iGbdTf1E750='))

