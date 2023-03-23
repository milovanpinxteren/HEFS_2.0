# import os
# import urllib.parse
#
# import django
# from redis import Redis
# from rq import Worker, Queue, Connection
#
# django.setup()
# listen = ['high', 'default', 'low']
#
# redis_url = os.getenv('REDIS_URL', 'localhost:6379')
#
# urllib.parse.uses_netloc.append('redis')
# url = urllib.parse.urlparse(redis_url)
# conn = Redis(host=url.hostname, port=url.port, db=0, password=url.password)
#
#
# if __name__ == '__main__':
#     # with Connection(conn):
#     #     worker = Worker(map(Queue, listen))
#     #     worker.work()
#     print("WORKER OPGESTART")
#     q = Queue(connection=Redis())





