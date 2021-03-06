"""flask插件形式的log设置组件.

## 基本的使用方法

```python
from log import FlaskSetLog
app = Flask(__name__)
run_aplication = FlaskSetLog(app)
```

或者使用默认的实例:
```python
from log import set_log

app = Flask(__name__)
set_log.init_app(app)
```

## 可以设置flask的了log配置

+ `SET_LOG_FMT:bool` 可以用于设置log的格式,目前支持json和txt
+ `SET_LOG_ERRORLOG:str` 可以设置服务器的log是否要输出到文本.默认为`-`,意为输出到stdout,其他则会写到字符串对应的文件名中.
    输出到文本则使用`TimedRotatingFileHandler`具体设置可以查看[官方文档](https://docs.python.org/3/library/logging.handlers.html#timedrotatingfilehandler)
    其他相关的参数还有:
    + `SET_LOG_ERRORLOG_WHEN:str` 默认'midnight',什么时候更新文件回卷
    + `SET_LOG_ERRORLOG_INTERVAL:int` 默认1,回卷间隔
    + `SET_LOG_ERRORLOG_BACKCOUNT:int` 默认3,保留多少个历史文件
    + `SET_LOG_ERRORLOG_ENCODING:str`: 默认"utf-8",使用什么编码保存
    + `SET_LOG_ERRORLOG_DELAY: 默认False, 是否延迟
    + `SET_LOG_ERRORLOG_UTC: 默认True,log回滚时间是否使用utc时间
    + `SET_LOG_ERRORLOG_ATTIME:str`:默认为None,使用格式"9,10,30"表示9点10分30秒
    + `SET_LOG_ERRORLOG_LOGLEVEL:int`默认"info",server的log等级

+ `SET_LOG_MAIL_LOG:bool`,可以设置app的logger是否要支持发送错误信息到邮箱,相关的其他参数还有:
    + `SET_LOG_MAILHOST:str` 默认为None,设置发送邮箱的地址
    + `SET_LOG_MAILPORT:int` 默认为25,设置发送邮箱的端口
    + `SET_LOG_MAILSSL:bool` 默认为False,设置发送邮箱是否使用ssl加密发送(25端口一般不加密,465端口一般加密)
    + `SET_LOG_MAILUSERNAME:str` 默认为None,设置发送邮箱的用户名
    + `SET_LOG_MAILPASSWORD:str` 默认为None,设置发送邮箱的密码
    + `SET_LOG_MAILFROMADDR:str` 默认为None,设置发送邮箱的地址
    + `SET_LOG_MAILTOADDRS:List[str]` 默认为None,设置要发送去的目标,注意是字符串列表
    + `SET_LOG_MAILSUBJECT:str` 默认为`Application Error`,设置发送去邮件的主题
"""
import time
import datetime
import logging
from logging.handlers import (
    TimedRotatingFileHandler,
    SMTPHandler
)
from flask import request
from flask.logging import default_handler
import werkzeug._internal as _internal
logging.Formatter.converter = time.gmtime


class RequestFormatter(logging.Formatter):
    def format(self, record):
        record.request = '{0} {1}'.format(request.method, request.url)
        record.host = request.host
        return super().format(record)


Formatters = {
    "access_json": RequestFormatter(** {
        "fmt": '''{"time":"%(asctime)s","name":"test_drone.server", "level":"%(levelname)s","host":"%(host)s","request":"%(request)s",%(message)s}''',
        "datefmt": "%Y-%m-%dT%H:%M:%S Z"
    }),
    "access_txt": RequestFormatter(** {
        "fmt": "[%(asctime)s] - (test_drone.server)[%(levelname)s]@[%(host)s] %(request)s: %(message)s",
        "datefmt": "%Y-%m-%dT%H:%M:%S Z"
    }),
    "server_txt": logging.Formatter(**{
        "fmt": '[%(asctime)s] [test_drone.server] %(levelname)s in %(module)s: %(message)s',
        "datefmt": "%Y-%m-%dT%H:%M:%S Z"
    }),
    "server_json": logging.Formatter(**{
        "fmt": '''{"time":"%(asctime)s","name":"test_drone.server", "level":"%(levelname)s","msg":"%(message)s"}''',
        "datefmt": "%Y-%m-%dT%H:%M:%S Z"
    })
}


def emit(self, record):
    try:
        import smtplib
        from email.message import EmailMessage
        import email.utils

        port = self.mailport
        if not port:
            port = smtplib.SMTP_PORT
        smtp = smtplib.SMTP_SSL(self.mailhost, port, timeout=self.timeout)
        msg = EmailMessage()
        msg['From'] = self.fromaddr
        msg['To'] = ','.join(self.toaddrs)
        msg['Subject'] = self.getSubject(record)
        msg['Date'] = email.utils.localtime()
        msg.set_content(self.format(record))
        if self.username:
            if self.secure is not None:
                smtp.ehlo()
                smtp.starttls(*self.secure)
                smtp.ehlo()
            smtp.login(self.username, self.password)
        smtp.send_message(msg)
        smtp.quit()
    except Exception:
        self.handleError(record)


def _init_logger(
        app,
        fmt="txt",
        errorlog="-",
        errorlog_when='midnight',
        errorlog_interval=1,
        errorlog_backupcount=3,
        errorlog_encoding="utf-8",
        errorlog_delay=False,
        errorlog_utc=True,
        errorlog_attime=None,
        loglevel="info",
        mail_log=False,
        mailhost=None,
        mailport=25,
        mailusername=None,
        mailpassword=None,
        mailssl=False,
        mailfromaddr=None,
        mailtoaddrs=None,
        mailsubject="Application Error"):
    """为flask项目设置logger

    Args:
        app ([type]): flask的app对象
        fmt (str, optional): Defaults to "json". log的格式
    """
    fmtRange = ("json", "txt")
    formatter = Formatters.get("access_" + fmt)
    default_handler.setFormatter(formatter)

    serverlogger = logging.getLogger('werkzeug')
    if errorlog == "-":
        server_handler = logging.StreamHandler()
    else:
        server_handler = TimedRotatingFileHandler(**{
            "filename": errorlog,
            "when": errorlog_when,
            "interval": errorlog_interval,
            "backupCount": errorlog_backupcount,
            "encoding": errorlog_encoding,
            "delay": errorlog_delay,
            "utc": errorlog_utc,
            "atTime": None if not errorlog_attime else datetime.time(*[int(i) for i in errorlog_attime.split(",")])
        })
    server_handler.setFormatter(Formatters.get("server_" + fmt))
    serverlogger.handlers = []
    serverlogger.addHandler(server_handler)
    serverlogger.setLevel(loglevel.upper())

    if mail_log is True:
        if mailport:
            mailhost = (mailhost, mailport)
        if mailssl:
            SMTPHandler.emit = emit
        if mailusername:
            if mailpassword:
                credentials = (mailusername, mailpassword)
            else:
                credentials = (mailusername,)
            mail_handler = SMTPHandler(
                mailhost=mailhost,
                fromaddr=mailfromaddr,
                toaddrs=mailtoaddrs,
                credentials=credentials,
                subject=mailsubject
            )
        else:
            mail_handler = SMTPHandler(
                mailhost=mailhost,
                fromaddr=mailfromaddr,
                toaddrs=mailtoaddrs,
                subject=mailsubject
            )
        mail_handler.setLevel("ERROR")
        mail_handler.setFormatter(formatter)
        if not app.debug:
            app.logger.addHandler(mail_handler)


class FlaskSetLog:
    """可以通过配置`SET_LOG_xxxx`来设置参数."""

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['setlog'] = self
        log_config = (app.config.get_namespace('SET_LOG_'))
        _init_logger(app=self.app, **log_config)


set_log = FlaskSetLog()
__all__ = ["FlaskSetLog", "set_log"]
