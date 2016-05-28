from interns.settings import interns_settings

from celery import Celery
app = Celery('tasks', broker='amqp://guest@{0}//'.format(interns_settings.rabbitmq_host))


@app.task
def add(x, y):
    return x + y

