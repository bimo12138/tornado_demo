import tornado.web
from model.models import Students, AuthInformation, Teachers, Exams, StudentToExam
import json
import os
from utils.base_utils import Result, authenticate, hashed, teacher_authenticate, TimeProcess
from files.file_manager import FileManager
from utils.email_utils import student_check


class BaseHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')


class StudentControl(BaseHandler):

    def get(self):
        no = self.get_argument("student_no")
        password = self.get_argument("password")
        if Students.is_exists(student_no=no):
            result = authenticate(no, password)
            if result:
                self.finish(Result.success("登陆成功！"))
            else:
                self.finish(Result.not_this_message(message="密码输入错误，请重试！"))
        else:
            self.finish(Result.not_this_message(message="当前学号不存在！请仔细检查，稍后再试"))

    def post(self):
        message = json.loads(self.request.body)
        no = message['student_no']
        username = message['student_name']
        password = message['password']
        if no and username and password:
            if Students.is_exists(student_no=no):
                self.finish(Result.already_register(message="该账号已经注册，请更换账号！"))
            else:
                Students.add_student(no, hashed(password))
                AuthInformation.initial(no, username)
                self.finish(Result.success(message="注册成功！"))
        else:
            self.finish(Result.not_this_message(message="信息输入不全面！请重新输入"))


class TeacherControl(BaseHandler):

    def get(self):
        no = self.get_argument("teacher_no")
        password = self.get_argument("password")
        if Teachers.is_exists(no):
            result = teacher_authenticate(no, password)
            if result:
                self.finish(Result.success(message="登陆成功！"))
            else:
                self.finish(Result.not_this_message(message="密码错误！"))
        else:
            self.finish(Result.not_this_message(message="这个账号未注册！"))

    def post(self):
        message = json.loads(self.request.body)
        teacher_no = message['teacher_no']
        teacher_name = message['teacher_name']
        password = message['password']
        email = message['email']
        if Teachers.is_exists(teacher_no):
            self.finish(Result.already_register(message="该用户已经注册"))
        else:
            result = Teachers.add_teacher(teacher_no, teacher_name, hashed(password), email)
            if result:
                self.finish(Result.success(message="信息添加成功！"))
            else:
                self.finish(Result.params_error(message="注册失败！参数出现错误，请重试！"))


class EmailControl(BaseHandler):

    def get(self):
        no = self.get_argument("student_no")
        result = Students.active_email(no)
        if result:
            self.finish(Result.success(message="尊敬的{}，您的邮箱已经激活！感谢您的使用！".format(no)))
        else:
            self.finish(Result.params_error(message="激活失败，请检查您的信息是否正确！"))

    def post(self):
        message = json.loads(self.request.body)
        no = message['student_no']
        email = message['email']
        result = Students.add_email(no, email)
        if result:
            email_send = student_check(email, no)
            if email_send:
                self.finish(Result.success(message="信息发出成功!邮箱添加成功！"))
            else:
                self.finish(Result.not_this_message(message="邮箱服务出现错误，不能提供服务，请谅解！"))
        else:
            self.finish(Result.params_error(message="邮箱已添加不必重复操作！"))


class SpecialtyControl(BaseHandler):

    def post(self):
        specialty_name = self.get_argument("specialty_name")
        if specialty_name:
            pass


class AuthInfoControl(BaseHandler):

    def get(self):
        auth_no = self.get_argument("auth_no")
        if AuthInformation.is_exists(auth_no):
            self.finish(Result.success(AuthInformation.get_auth_info(auth_no)))
        else:
            self.finish(Result.not_this_message(message="当前用户不存在数据库中！请核实后再访问！"))

    def post(self):
        message = json.loads(self.request.body)
        auth_no = message['auth_no']
        detail = message['detail']
        result = AuthInformation.change_base_information(auth_no, detail=detail)
        if result:
            self.finish(Result.success(message="信息修改成功！"))
        else:
            self.finish(Result.params_error(message="参数错误，请重试！"))


class ExamControl(BaseHandler):

    def get(self):
        author = self.get_argument("username")
        result = Exams.get_exam(author)
        if result:
            self.finish(Result.success(message=json.loads(result)))
        else:
            self.finish(Result.params_error(message="出现错误！"))

    def post(self):
        files = self.request.files.get("file", None)
        exam_name = str(*self.request.body_arguments.get("exam_name"), encoding="utf-8")
        start_time = str(*self.request.body_arguments.get("start_time"), encoding="utf-8")
        end_time = str(*self.request.body_arguments.get("end_time"), encoding="utf-8")
        last = str(*self.request.body_arguments.get("last"), encoding="utf-8")
        score = str(*self.request.body_arguments.get("score"), encoding="utf-8")
        author = str(*self.request.body_arguments.get("author"), encoding="utf-8")
        if exam_name and start_time and end_time and last and score and author:
            start_timestamp = TimeProcess.save_to_table(start_time)
            end_timestamp = TimeProcess.save_to_table(end_time)
            if files:
                for file in files:
                    filename = file['filename']
                    name, exp = os.path.splitext(filename)
                    file_control = FileManager()
                    result = file_control.add_files(file['body'], exp, exam_name, author, filename, start_timestamp, end_timestamp, last, score)
                    if result:
                        self.finish(Result.success(message="试卷上传成功！"))
                    else:
                        self.finish(Result.params_error(message="信息写入错误！"))
            else:
                self.finish(Result.not_this_message(message="文件上传错误！请重试！"))
        else:
            self.finish(Result.params_error(message="参数信息不全, 请修改后重新上传"))

    def delete(self):
        exam_no = self.get_argument("exam_no")
        result = Exams.delete_exam(exam_no)
        if result:
            self.finish(Result.success(message="删除成功！"))
        else:
            self.finish(Result.params_error(message="删除错误，请刷新后重试！"))


class ExamExplore(BaseHandler):

    # 获取试卷详情
    def get(self):
        exam_no = self.get_argument("exam_no")
        result = json.loads(str(Exams.get_exam_detail(exam_no)))
        if result:
            self.finish(Result.success(message=result))
        else:
            self.finish(Result.not_this_message(message="信息查询错误，请重试！"))


class ActiveExam(BaseHandler):

    def get(self):
        response = Exams.get_valid_exam()
        if response:
            result = [json.loads(str(i)) for i in response]
            return self.finish(Result.success(message=result))
        else:
            return self.finish(Result.not_this_message(message="没有可以参加的考试！"))


class TakeExam(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def get(self):
        exam_no = self.get_argument("exam_no")
        student_no = self.get_argument("student_no")
        if StudentToExam.is_exists(student_no, exam_no):
            result = StudentToExam.get_content(student_no, exam_no)
            if result:
                self.finish(Result.success(message=result))
            else:
                self.finish(Result.params_error(message="您不能参加本次考试！"))
        else:
            result = StudentToExam.add_content(student_no, exam_no)
            if result:
                self.finish(Result.success(message=str([*result])))
            else:
                self.finish(Result.params_error(message="数据错误，请重试！"))

    def post(self):
        message = json.loads(self.request.body)
        student_no = message['student_no']
        exam_no = message['exam_no']
        content = message['content']
        if StudentToExam.is_exists(student_no=student_no, exam_no=exam_no):
            result = StudentToExam.submit(student_no=student_no, exam_no=exam_no, content=content)
            if result:
                self.finish(Result.success(message="提交成功！"))
            else:
                self.finish(Result.params_error(message="提交错误，请重试！"))

    def put(self):
        message = json.loads(self.request.body)
        student_no = message['student_no']
        exam_no = message['exam_no']
        content = message['content']
        if StudentToExam.is_exists(student_no=student_no, exam_no=exam_no):
            result = StudentToExam.temp_save(student_no=student_no, exam_no=exam_no, content=content)
            if result:
                self.finish(Result.success(message="提交成功！"))
            else:
                self.finish(Result.params_error(message="提交错误，请重试！"))


class GetEmailStatus(BaseHandler):

    def get(self):
        result = Students.is_active(self.get_argument("student_no"))
        if result:
            self.finish(Result.success(message="邮箱激活成功！"))
        else:
            self.finish(Result.not_this_message(message="未激活"))


class GetAlreadyAttendExam(BaseHandler):

    def get(self):
        student_no = self.get_argument("student_no")
        result = StudentToExam.get_attend_exam(student_no)
        if result:
            self.finish(Result.success(message=str(*result)))
        else:
            self.finish(Result.params_error(message="获取失败！"))


class LoadingExam(BaseHandler):

    def get(self):
        exam_no = self.get_argument("exam_no")
        result = StudentToExam.get_attended_exam(exam_no)
        if result:
            self.finish(Result.success(message=str(*result)))
        else:
            self.finish(Result.not_this_message(message="数据错误！"))


class EvaluateExam(BaseHandler):

    def get(self):
        exam_no = self.get_argument("exam_no")
        student_no = self.get_argument("student_no")
        result = StudentToExam.evaluate_exam(exam_no=exam_no, student_no=student_no)
        if result:
            self.finish(Result.success(message=result))
        else:
            self.finish(Result.not_this_message(message="信息获取错误！"))

    def post(self):
        exam_no = self.get_argument("exam_no")
        student_no = self.get_argument("student_no")
        score = self.get_argument("score")
        result = StudentToExam.get_score(exam_no, student_no, score)
        if result:
            self.finish(Result.success(message="成功@A@"))
        else:
            self.finish(Result.not_this_message(message="信息传输失败QAQ!"))


class Rank(BaseHandler):

    def get(self):
        exam_no = self.get_argument("exam_no")
        result = StudentToExam.get_rank(exam_no)
        if result:
            self.finish(Result.success(message=str([*result])))
        else:
            self.finish(Result.not_this_message(message="还没人参加考试哦！"))


class GetExamList(BaseHandler):

    def get(self):

        result = Exams.get_exams()
        if result:
            self.finish(Result.success(message=str([*result])))
        else:
            self.finish(Result.not_this_message(message="信息传输失败QAQ!"))
