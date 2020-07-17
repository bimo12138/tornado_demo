"""
@author:      13716
@date-time:   2019/7/1-19:17
@ide:         PyCharm
@name:        base_utils.py
"""
import hashlib
import uuid
from model.models import Students, Teachers
import time
import base64
import time
import hmac


def hashed(text):
    return hashlib.md5(text.encode()).hexdigest()


class GetUuid(object):

    @classmethod
    def get_time_uuid(cls):
        return uuid.uuid1().hex

    @classmethod
    def get_name_uuid(cls, text):
        return uuid.uuid3(uuid.NAMESPACE_DNS, text).hex

    @classmethod
    def get_name_uuid_5(cls, text):
        return uuid.uuid5(uuid.NAMESPACE_DNS, text).hex

    @classmethod
    def get_random_uuid(cls):
        return uuid.uuid4().hex


class Token(object):

    # 分类 0 学生 1 老师
    @classmethod
    def get_token(cls, classify, no):
        cls.key = b"rsmrtxcsnmzj.zyxczpc.hwjz"
        header = {
            "alg": "HS256"
        }
        b_header = base64.b64encode(str(header).encode("utf-8"))
        if classify == 0:

            payload = {
                "iss": "笔墨",
                "iat": Students.get_last_time(no)
            }

            b_pay_load = base64.b64encode(str(payload).encode("utf-8"))
            code = hmac.new(cls.key, b_header + b"." + b_pay_load, digestmod="MD5")
            return code.hexdigest()
        elif classify == 1:
            payload = {
                "iss": "笔墨",
                "iat": Teachers.get_last_time(no)
            }

            b_pay_load = base64.b64encode(str(payload).encode("utf-8"))
            code = hmac.new(cls.key, b_header + b"." + b_pay_load, digestmod="MD5")
            return code.hexdigest()

    @classmethod
    def check_token(cls, token, classify, no):
        cls.key = b"rsmrtxcsnmzj.zyxczpc.hwjz"
        header = {
            "alg": "HS256"
        }
        b_header = base64.b64encode(str(header).encode("utf-8"))
        if classify == 0:

            payload = {
                "iss": "笔墨",
                "iat": Students.get_last_time(no)
            }

            b_pay_load = base64.b64encode(str(payload).encode("utf-8"))
            code = hmac.new(cls.key, b_header + b"." + b_pay_load, digestmod="MD5")
            return code.hexdigest() == token
        elif classify == 1:
            payload = {
                "iss": "笔墨",
                "iat": Teachers.get_last_time(no)
            }

            b_pay_load = base64.b64encode(str(payload).encode("utf-8"))
            code = hmac.new(cls.key, b_header + b"." + b_pay_load, digestmod="MD5")
            return code.hexdigest() == token


def authenticate(username, password):
    if username and password:
        password_data = Students.get_password(username)
        if password_data and password_data == hashed(password):
            return True
        else:
            return False


def teacher_authenticate(username, password):
    if username and password:
        if hashed(password) == Teachers.get_password(username):
            return True
        else:
            return False


class Result(object):

    @classmethod
    def not_this_message(cls, message=""):
        message_json = {
            "code": 400,
            "message": message
        }
        return message_json

    @classmethod
    def success(cls, message):
        message_json = {
            "code": 200,
            "message": message
        }
        return message_json

    @classmethod
    def already_register(cls, message):
        message_json = {
            "code": 416,
            "message": message
        }
        return message_json

    @classmethod
    def params_error(cls, message):
        message_json = {
            "code": 403,
            "message": message
        }
        return message_json


def time_load(raw_time):
    week_day, mouth, day, year, de_time, zone, desc = raw_time.split(" ")
    hour, minute, second = de_time.split(":")
    return " ".join([year, mouth, day, hour, minute, second, week_day])


class TimeProcess(object):
    """
        存入数据库使用 时间戳
        读取之后 设置一个刻度模式，但是考试验证依然使用时间戳
        记住时间戳要进行取整
        "Tue Jul 02 2019 08:00:00 GMT+0800 (中国标准时间)"
    """
    @classmethod
    def save_to_table(cls, raw_string):
        trans_string = time_load(raw_string)
        decode_time = "%Y %b %d %H %M %S %a"
        timestamp = int(time.mktime(time.strptime(trans_string, decode_time)))
        return timestamp

    @classmethod
    def to_load(cls, timestamp):
        return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(timestamp))))
