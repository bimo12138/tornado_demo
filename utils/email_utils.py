"""
@author:      13716
@date-time:   2019/7/12-17:59
@ide:         PyCharm
@name:        email_utils.py
"""

import smtplib
from email.mime.text import MIMEText
from email.header import Header

sender = '1371639183@qq.com'
password = "njvpudkxtonpgjjf"
subject = "智能校园服务--"


def student_check(receive, no):
    mail_message = """
        <div style="width: 80%; margin: 0 auto;">
            <h3 style="text-align: center; background: yellowgreen;">智能校园服务 -- 邮箱认证</h3>
                <p>您好！您的账号授权邮箱为: <br> <a href="{}">点此链接</a></p>
            <h3 style="color: red">请勿回复, 谢谢！</h3>
        </div>
    """.format("http://127.0.0.1:8081/email?email=" + receive + "&student_no=" + no)

    subject_student_check = subject + "学生认证"
    mail = MIMEText(mail_message, 'html', 'utf-8')
    mail['From'] = Header(sender)
    mail['to'] = Header(receive)
    mail['Subject'] = Header(subject_student_check, 'utf-8')
    try:
        s = smtplib.SMTP_SSL('smtp.qq.com', 465)
        s.login(sender, password)
        s.sendmail(sender, receive, mail.as_string())
        s.quit()
        return True
    except Exception:
        print("邮箱服务器出现错误！")
        return False


def teacher_check(receive, no):
    mail_message = """
            <div style="width: 80%; margin: 0 auto;">
                <h3 style="text-align: center; background: yellowgreen;">智能校园服务 -- 邮箱认证</h3>
                    <p>您好！您的账号授权邮箱为: <br> <a href="{}">点此链接</a></p>
                <h3 style="color: red">请勿回复, 谢谢！</h3>
            </div>
        """.format("http://127.0.0.1:8081/email?email=" + receive + "&student_no=" + no)

    subject_student_check = subject + "学生认证"
    mail = MIMEText(mail_message, 'html', 'utf-8')
    mail['From'] = Header(sender)
    mail['to'] = Header(no)
    mail['Subject'] = Header(subject_student_check, 'utf-8')

    try:
        s = smtplib.SMTP_SSL('smtp.qq.com', 465)
        s.login(sender, password)
        s.sendmail(sender, no, mail.as_string())
        s.quit()
        return True

    except Exception:
        return False


if __name__ == "__main__":
    student_check("1371639183@qq.com", "10001")
