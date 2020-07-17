"""
@author:      13716
@date-time:   2019/7/25-23:18
@ide:         PyCharm
@name:        file_manager.py
"""
import glob
from utils.base_utils import GetUuid
from model.models import Exams, TitleCompare
import xlrd, os, json


class FileManager(object):

    def __init__(self):
        all_list = []
        all_list += glob.glob("*.xlsx")
        all_list += glob.glob("*.xls")

    def add_files(self, content, exp, exam_name, author, raw_name, start_time, end_time, last, score):
        name = GetUuid.get_time_uuid()
        file_name = name + exp
        with open("files/{}".format(file_name), "wb") as f:
            f.write(content)

        work_book = xlrd.open_workbook(os.path.join(os.getcwd(), "files\\", file_name))
        sheet = work_book.sheet_by_index(0)
        rows = sheet.nrows
        exam_number = rows - 1
        cols = sheet.ncols
        if cols == 9:
            choose_list = []
            input_list = []
            judge_list = []
            subjective_list = []
            for i in range(1, rows):

                data_list = sheet.row_values(i)
                classify, no, title, a, b, c, d, correct, analyse = data_list
                if classify == 1:
                    question = {
                        "classify": 1,
                        "no": no,
                        "title": title,
                        "A": a,
                        "B": b,
                        "C": c,
                        "D": d,
                        "correct": correct,
                        "analyse": analyse
                    }
                    choose_list.append(question)
                elif classify == 2:
                    question = {
                        "classify": 2,
                        "no": no,
                        "title": title,
                        "correct": correct,
                        "analyse": analyse
                    }
                    input_list.append(question)
                elif classify == 3:
                    question = {
                        "classify": 3,
                        "no": no,
                        "title": title,
                        "correct": correct,
                        "analyse": analyse
                    }
                    judge_list.append(question)
                else:
                    question = {
                        "classify": 4,
                        "no": no,
                        "title": title,
                        "correct": correct,
                        "analyse": analyse
                    }
                    subjective_list.append(question)
            question_dict = {
                "choose_list": choose_list,
                "input_list": input_list,
                "judge_list": judge_list,
                "subjective_list": subjective_list
            }

            if Exams.add_exam(exam_name, author, raw_name, start_time, end_time, last, score, json.dumps(question_dict)):
                return True
            else:
                return False

        else:
            return False
