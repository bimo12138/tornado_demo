"""
@author:      13716
@date-time:   2019/6/29-13:42
@ide:         PyCharm
@name:        models.py
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, text, Table, and_, desc
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship, backref
from .db import Base, session
import json
import time
from sqlalchemy.sql import exists
import re


def deal_question(question_list):
    message = []
    for i in question_list:
        if isinstance(i, dict):
            messages = i
        else:
            messages = json.loads(i)

        if messages['classify'] == 1:
            message.append({
                "classify": i['classify'],
                "no": int(i['no']),
                "title": i['title'],
                "A": i['A'],
                "B": i['B'],
                "C": i['C'],
                "D": i['D'],
                "answer": ""
            })
        else:
            message.append({
                "classify": i['classify'],
                "no": int(i['no']),
                "title": i['title'],
                "answer": ""
            })

    return message


def num_to_char(num):
    if num == 1:
        return "A"
    elif num == 2:
        return "B"
    elif num == 3:
        return "C"
    elif num == 4:
        return "D"
    else:
        return False


def num_to_boolean(num):
    return True if num == 1 else False


def sort_char(element):
    return element[0]


class Students(Base):

    __tablename__ = "Students"

    student_no = Column(String(20), primary_key=True)
    last_login = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    password = Column(String(80), nullable=False)
    email = Column(String(60), nullable=True)
    email_active = Column(Boolean, default=False)
    info = relationship("AuthInformation", backref=backref("Students", uselist=False))

    def __repr__(self):
        return self.student_no

    def __str__(self):
        return self.student_no

    @classmethod
    def is_exists(cls, student_no):
        return session.query(exists().where(Students.student_no == student_no)).scalar()

    @classmethod
    def get_password(cls, student_no):
        student = session.query(cls).filter_by(student_no=student_no).one()
        if student:
            return student.password
        else:
            return False

    @classmethod
    def add_student(cls, no, password):

        added_student = Students(student_no=no, password=password)
        session.add(added_student)
        result = session.commit()
        return result

    @classmethod
    def change_password(cls, student_no, new_password):
        student = session.query(cls).filter_by(student_no=student_no)
        if student:
            student.update({"password": new_password})
            try:
                session.commit()
                return True
            except:
                return False
        else:
            return False

    @classmethod
    def add_email(cls, no, email):
        student = session.query(cls).filter_by(student_no=no)
        if student.one().email:
            return False
        else:
            student = student.update({"email": email})
            if student:
                try:
                    session.commit()
                    return True
                except:
                    return False
            else:
                return False

    @classmethod
    def is_active(cls, no):
        student = session.query(cls).filter_by(student_no=no).one()
        if student.email_active:
            return True
        else:
            return False

    @classmethod
    def active_email(cls, no):
        student = session.query(cls).filter_by(student_no=no)
        if student.one().email_active:
            return False
        else:
            student.update({"email_active": True})
            session.commit()
            return True

    @classmethod
    def check_email(cls, no, email):
        if session.query(cls).filter_by(student_no=no).one().email == email:
            return True
        else:
            return False

    @classmethod
    def get_information(cls, no):
        return session.query(cls).filter_by(student_no=no).one().info[0]

    @classmethod
    def get_last_time(cls, no):
        return session.query(cls).filter_by(student_no=no).one().last_login


# 学生信息
class AuthInformation(Base):

    __tablename__ = "AuthInformation"

    auth_no = Column(String(20), ForeignKey("Students.student_no"), primary_key=True)
    auth_name = Column(String(10))
    birthday = Column(DateTime, nullable=True, default=date.today())
    # 0 私密 1 男 2 女
    sex = Column(Integer, default=0)
    grade = Column(Integer, default=datetime.now().year)
    id = Column(String(18), nullable=True)
    address = Column(String(50), nullable=True)

    def __repr__(self):
        message = {
            "auth_name": self.auth_name,
            "birthday": str(self.birthday),
            "sex": self.sex,
            "id": self.id,
            "address": self.address
        }
        return json.dumps(message)

    def __str__(self):
        return self.auth_no

    @classmethod
    def initial(cls, auth_no, auth_name):
        initial_information = AuthInformation(auth_no=auth_no, auth_name=auth_name)
        session.add(initial_information)
        try:
            session.commit()
            return True
        except:
            return False

    @classmethod
    def change_name(cls, auth_no, auth_name):
        auth = session.query(cls).filter_by(auth_no=auth_no)
        if auth:
            auth.update({"auth_name": auth_name})
            session.commit()
            return True
        else:
            return False

    @classmethod
    def is_exists(cls, auth_no):
        return session.query(exists().where(cls.auth_no == auth_no)).scalar()

    @classmethod
    def get_auth_info(cls, auth_no):
        auth_info = session.query(cls).filter_by(auth_no=auth_no).one()
        message = {
            "auth_name": auth_info.auth_name,
            "birthday": str(auth_info.birthday),
            "sex": auth_info.sex,
            "id": auth_info.id,
            "address": auth_info.address
        }
        return message

    @classmethod
    def change_base_information(cls, auth_no, **kwargs):
        auth = session.query(cls).filter_by(auth_no=auth_no)
        if auth:
            updated = {}
            for i in kwargs["detail"]:
                updated[i] = kwargs["detail"][i]

            auth.update(updated)
            try:
                session.commit()
                return True
            except:
                return False
        else:
            return False


# 老师
class Teachers(Base):

    __tablename__ = "Teachers"
    teacher_no = Column(String(10), primary_key=True)
    teacher_name = Column(String(10))
    last_login = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    password = Column(String(80), nullable=False)
    email = Column(String(30), nullable=True)

    def __repr__(self):
        return self.teacher_no

    def __str__(self):
        return self.teacher_no

    @classmethod
    def is_exists(cls, teacher_no):
        return session.query(exists().where(cls.teacher_no == teacher_no)).scalar()

    @classmethod
    def get_password(cls, teacher_no):
        teacher = session.query(cls).filter_by(teacher_no=teacher_no).one()
        return teacher.password

    @classmethod
    def add_teacher(cls, no, name, password, email):
        teacher = Teachers(teacher_no=no, teacher_name=name, password=password, email=email)
        session.add(teacher)
        try:
            session.commit()
            return True
        except:
            return False

    @classmethod
    def get_last_time(cls, no):
        return session.query(cls).filter_by(teacher_no=no).one().last_login


# 考试基本信息
class Exams(Base):

    __tablename__ = "Exams"
    exam_no = Column(Integer, primary_key=True, autoincrement=True)
    exam_name = Column(String(30))
    exam_author = Column(String(10), ForeignKey("Teachers.teacher_no"), nullable=False)
    exam_body = Column(LONGTEXT)
    raw_files = Column(String(50))
    start_time = Column(String(20))
    end_time = Column(String(20))
    exam_time = Column(Integer, default=120)
    score_count = Column(Integer, default=100)
    upload_time = Column(DateTime, default=datetime.now())

    def __repr__(self):
        message = {
            "exam_no": self.exam_no,
            "exam_name": self.exam_name,
            "start_time": str(self.start_time),
            "end_time": str(self.end_time),
            "exam_time": self.exam_time,
            "score_count": self.score_count,
            "upload_time": str(self.upload_time)
        }
        return json.dumps(message)

    def __str__(self):
        message = {
            "exam_no": self.exam_no,
            "exam_name": self.exam_name,
            "start_time": str(self.start_time),
            "end_time": str(self.end_time),
            "exam_time": self.exam_time,
            "score_count": self.score_count,
            "upload_time": str(self.upload_time)
        }
        return json.dumps(message)

    @classmethod
    def add_exam(cls, name, author, raw, start, end, last, count, exam_body):
        exam = Exams(exam_name=name, exam_author=author, raw_files=raw, start_time=start, end_time=end, exam_time=last, score_count=count, exam_body=exam_body)
        session.add(exam)
        try:
            session.commit()
            return True
        except:
            return False

    @classmethod
    def get_exam(cls, author):
        result = session.query(cls).filter_by(exam_author=author).all()
        return str(result)

    @classmethod
    def delete_exam(cls, exam_no):
        result = session.query(cls).filter_by(exam_no=exam_no).delete()
        if result:
            session.commit()
            return result
        else:
            return False

    @classmethod
    def get_exam_detail(cls, exam_no):
        exam = session.query(cls).filter_by(exam_no=exam_no).one()
        get_time = int(time.time())

        if get_time > int(exam.start_time):
            if get_time < int(exam.end_time):
                status = "考试进行中"
            else:
                status = "考试已结束"
        else:
            status = "考试未开始"

        exam_detail = {
            "exam_name": exam.exam_name,
            "status": status,
            "exam_body": exam.exam_body
        }

        if exam_detail:
            return json.dumps(exam_detail)

        else:
            return False

    @classmethod
    def get_valid_exam(cls):
        result = session.query(cls).all()
        if result:
            return result
        else:
            return False

    @classmethod
    def get_detail_exam(cls, exam_no):
        result = session.query(cls).filter_by(exam_no=exam_no).one()
        if result:
            return result.students
        else:
            return False

    @classmethod
    def add_new_exam_situation(cls, student_no, exam_no):
        student = session.query(Students).filter_by(student_no=student_no).one()
        exam = session.query(Exams).filter_by(exam_no=exam_no).one()

        if student and exam:
            student.exam = [exam]
            session.add(student)
            session.commit()
            return True
        else:
            return False

    @classmethod
    def get_exam_content(cls, exam_no, student_no):
        if cls.is_exists(exam_no, student_no):
            result = session.query(cls).filter(and_(exam_no == exam_no, student_no == student_no)).one()
            if result:
                return result.exam_body
            else:
                return False
        else:
            # 开始抽题
            exam_name = session.query(cls).filter_by(exam_no=exam_no).one()
            content = exam_name.exam_body
            if not isinstance(content, dict):
                content = dict(eval(content))

            choose_list = content['choose_list']
            choose_list_len = len(choose_list)
            input_list = content['input_list']
            input_list_len = len(input_list)
            judge_list = content['judge_list']
            judge_list_len = len(judge_list)
            subjective_list = content['subjective_list']
            subjective_list_len = len(subjective_list)

            if choose_list_len >= 50 and input_list_len >= 10 and judge_list_len >= 10 and subjective_list_len >= 3:
                # 方案一
                import random

                choose_num_list = random.sample(choose_list, 50)
                choose_num_list = deal_question(choose_num_list)
                input_num_list = random.sample(input_list, 10)
                input_num_list = deal_question(input_num_list)
                judge_num_list = random.sample(judge_list, 10)
                judge_num_list = deal_question(judge_num_list)
                subjective_num_list = random.sample(subjective_list, 3)
                subjective_num_list = deal_question(subjective_num_list)
                get_content = {
                    "choose_list": choose_num_list,
                    "input_list": input_num_list,
                    "judge_list": judge_num_list,
                    "subjective_list": subjective_num_list
                }
                student = session.query(Students).filter_by(student_no=student_no).one()
                exam_name.students.append(student)
                exam_name.answer_status.append(json.dumps(get_content))

                session.add(exam_name)
                session.commit()
                return content
            else:
                print("格式不正确")
                return False

    @classmethod
    def is_exists(cls, exam_no, student_no):
        for i in session.query(cls).filter_by(exam_no=exam_no).all():
            if str(i.students) == student_no:
                return True
        return False

    @classmethod
    def get_exams(cls):
        result = session.query(cls).all()

        if result:
            return result
        else:
            return False


class StudentToExam(Base):
    __tablename__ = "student_exam"
    student_no = Column(String(20), ForeignKey("Students.student_no", ondelete="CASCADE"), primary_key=True)
    exam_no = Column(Integer, ForeignKey("Exams.exam_no", ondelete="CASCADE"), primary_key=True)
    students = relationship(Students, backref="StudentToExam")
    exam = relationship(Exams, backref="Exams")
    score = Column(Integer, nullable=True)
    answer_status = Column(LONGTEXT)
    status = Column(Boolean, default=False)

    def __str__(self):
        return json.dumps({
            'student_no': self.student_no,
            "exam_no": self.exam_no,
            "status": self.status,
            "score": self.score
        })

    def __repr__(self):
        return json.dumps({
            'student_no': self.student_no,
            "exam_no": self.exam_no,
            "status": self.status,
            "score": self.score
        })

    @classmethod
    def is_exists(cls, student_no, exam_no):
        return session.query(cls).filter(and_(cls.student_no == student_no, cls.exam_no == exam_no)).one_or_none()

    @classmethod
    def get_content(cls, student_no, exam_no):
        result = session.query(cls).filter(and_(cls.student_no == student_no, cls.exam_no == exam_no)).one()
        if result:
            if result.status == 0:
                return result.answer_status
            else:
                return False
        else:
            return False

    @classmethod
    def add_content(cls, student_no, exam_no):
        # 开始抽题
        exam = session.query(Exams).filter_by(exam_no=exam_no).one()
        student = session.query(Students).filter_by(student_no=student_no).one()
        if not (exam and student):
            return False

        content = exam.exam_body
        if isinstance(content, dict):
            pass
        else:
            content = dict(eval(content))
            choose_list = content['choose_list']
            choose_list_len = len(choose_list)
            input_list = content['input_list']
            input_list_len = len(input_list)
            judge_list = content['judge_list']
            judge_list_len = len(judge_list)
            subjective_list = content['subjective_list']
            subjective_list_len = len(subjective_list)

            if choose_list_len >= 50 and input_list_len >= 10 and judge_list_len >= 10 and subjective_list_len >= 3:
                # 方案一
                import random

                choose_num_list = random.sample(choose_list, 50)
                choose_num_list = deal_question(choose_num_list)
                input_num_list = random.sample(input_list, 10)
                input_num_list = deal_question(input_num_list)
                judge_num_list = random.sample(judge_list, 10)
                judge_num_list = deal_question(judge_num_list)
                subjective_num_list = random.sample(subjective_list, 3)
                subjective_num_list = deal_question(subjective_num_list)
                get_content = {
                    "choose_list": choose_num_list,
                    "input_list": input_num_list,
                    "judge_list": judge_num_list,
                    "subjective_list": subjective_num_list
                }

                result = StudentToExam(exam_no=exam_no, student_no=student_no, answer_status=json.dumps(get_content))
                session.add(result)
                session.commit()
                return result
            else:
                print("格式不正确")
                return False

    @classmethod
    def temp_save(cls, student_no, exam_no, content):
        result = session.query(cls).filter(and_(cls.student_no == student_no, cls.exam_no == exam_no)).one()
        if result and result.status == 0:
            if isinstance(content, str):
                pass
            elif isinstance(content, dict):
                content = json.dumps(content)
            else:
                return False
            result.answer_status = content
            session.add(result)
            session.commit()
            return True
        else:
            return False

    @classmethod
    def submit(cls, student_no, exam_no, content):
        result = session.query(cls).filter(and_(cls.student_no == student_no, cls.exam_no == exam_no)).one()
        if result and result.status == 0:
            if isinstance(content, str):
                pass
            elif isinstance(content, dict):
                content = json.dumps(content)
            else:
                return False
            result.answer_status = content
            result.status = True
            session.add(result)
            session.commit()
            return True
        else:
            return False

    @classmethod
    def get_attend_exam(cls, student_no):
        result = session.query(cls).filter_by(student_no=student_no).all()
        if result:
            return result
        else:
            return False

    @classmethod
    def get_attended_exam(cls, exam_no):
        result = session.query(cls).filter(and_(cls.exam_no == exam_no, cls.status)).all()
        if result:
            return result
        else:
            return False

    @classmethod
    def evaluate_exam(cls, exam_no, student_no):
        content = session.query(cls).filter(and_(cls.exam_no == exam_no, cls.student_no == student_no)).one().answer_status
        raw_content = session.query(Exams).filter(and_(Exams.exam_no == exam_no)).one().exam_body

        if not isinstance(content, dict) or not isinstance(raw_conetent, dict):
            content = json.loads(content)
            raw_content = json.loads(raw_content)
        choose_list = content['choose_list']
        raw_choose_list = raw_content['choose_list']
        choose_score = 0
        judge_list = content['judge_list']
        raw_judge_list = raw_content['judge_list']
        judge_score = 0
        input_list = content['input_list']
        raw_input_list = raw_content['input_list']
        input_score = 0

        choose_tuple = [(choose_list[i]['no'], num_to_char(choose_list[i]["answer"])) for i in range(len(choose_list))]
        judge_list = [(judge_list[i]['no'], num_to_boolean(judge_list[i]["answer"])) for i in range(len(judge_list))]
        input_list = [(input_list[i]['no'], str(input_list[i]["answer"]).strip()) for i in range(len(judge_list))]

        raw_choose_tuple = [(raw_choose_list[i]['no'], raw_choose_list[i]["correct"]) for i in range(len(raw_choose_list))]
        raw_judge_tuple = [(raw_judge_list[i]['no'], raw_judge_list[i]["correct"]) for i in range(len(raw_judge_list))]
        raw_input_tuple = [(raw_input_list[i]['no'], str(raw_input_list[i]["correct"]).strip()) for i in range(len(raw_input_list))]

        for i in choose_tuple:
            index = i[0]
            if i[1] == raw_choose_tuple[index - 1][1]:
                choose_score += 1

        for j in judge_list:
            index = j[0]
            if j[1] == raw_judge_tuple[index - 1][1]:
                judge_score += 1

        for k in input_list:
            index = k[0]
            if k[1] == raw_input_tuple[index - 1][1]:
                input_score += 1

        message = {
            "choose_score": choose_score,
            "judge_score": judge_score,
            "input_score": input_score,
            "subjective_list": content['subjective_list'],
            "subjective_answer": json.loads(session.query(Exams).filter_by(exam_no=exam_no).one().exam_body)['subjective_list']
        }
        return message

    @classmethod
    def get_score(cls, exam_no, student_no, score):
        result = session.query(cls).filter(and_(cls.exam_no == exam_no, cls.student_no == student_no)).one()
        if result:
            result.score = score
            session.add(result)
            session.commit()
            return True
        else:
            return False

    @classmethod
    def get_rank(cls, exam_no):
        result = session.query(cls).filter_by(exam_no=exam_no).order_by(cls.score.desc()).limit(5).all()
        if result:
            return result
        else:
            return False


# 不用于大题目|| 性能太差，删掉
class TitleCompare(Base):
    __tablename__ = "title_compare"
    question_id = Column(Integer, primary_key=True, autoincrement=True)
    exam_no = Column(Integer, ForeignKey(Exams.exam_no, ondelete="CASCADE"), unique=False)
    classify = Column(Integer)
    question_no = Column(String(5))
    answer = Column(String(50))

    def __str__(self):
        return json.dumps({
            'exam_no': self.exam_no,
            "classify": self.classify,
            "question_no": self.question_no,
            "answer": self.answer
        })

    def __repr__(self):
        return json.dumps({
            'exam_no': self.exam_no,
            "classify": self.classify,
            "question_no": self.question_no,
            "answer": self.answer
        })

    @classmethod
    def is_exists(cls, exam_no, classify, question_no):
        return session.query(cls).filter(and_(cls.exam_no == exam_no, cls.classify == classify, cls.question_no == question_no)).one_or_none()

    @classmethod
    def add_row(cls, exam_no, classify, question_no, answer):
        if cls.is_exists(exam_no, classify, question_no):
            return False
        else:
            result = TitleCompare(exam_no=exam_no, classify=classify, question_no=question_no, answer=answer)
            session.add(result)
            session.commit()
            return True

    @classmethod
    def get_row(cls, exam_no, classify, question_no):
        result = session.query(cls).filter(
            and_(cls.exam_no == exam_no, cls.classify == classify, cls.question_no == question_no)).one_or_none()
        if result:
            return result.answer
        else:
            return None

    @classmethod
    def compare(cls, exam_no, classify, question_no, user_answer):

        if classify == 1:
            if user_answer == 1:
                user_answer = "A"
            elif user_answer == 2:
                user_answer = "B"
            elif user_answer == 3:
                user_answer = "C"
            elif user_answer == 4:
                user_answer = "D"
            else:
                user_answer = ""
            result = cls.get_row(exam_no, classify, question_no)
            if result == user_answer:
                return True
            else:
                return False

        elif classify == 2:
            if str(user_answer - 1) == str(cls.get_row(exam_no, classify, question_no)):
                return True
            else:
                return False

        elif classify == 3:
            if str(cls.get_row(exam_no, classify, question_no)).strip() == str(user_answer).strip():
                return True
            else:
                return False


