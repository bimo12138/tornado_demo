import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
from handlers import main

define("port", default="8081", help="监听的端口", type=int)


class Application(tornado.web.Application):

    def __init__(self):

        handlers = [
            ("/student", main.StudentControl),
            ("/email", main.EmailControl),
            ("/auth", main.AuthInfoControl),
            ("/teacher", main.TeacherControl),
            ("/exam", main.ExamControl),
            ("/exam_detail", main.ExamExplore),
            ("/active_exam", main.ActiveExam),
            ("/email_status", main.GetEmailStatus),
            ("/take_exam", main.TakeExam),
            ("/select_exam", main.GetAlreadyAttendExam),
            ("/loading_exam", main.LoadingExam),
            ("/evaluate_exam", main.EvaluateExam),
            ("/rank", main.Rank),
            ("/exam_list", main.GetExamList)
        ]

        settings = dict(
            debug=True,
            template_path="templates",
        )

        super(Application, self).__init__(handlers, **settings)


application = Application()

if __name__ == "__main__":

    tornado.options.parse_command_line()
    application.listen(options.port)
    print("请访问 http://127.0.0.1:8081/")
    tornado.ioloop.IOLoop.current().start()

