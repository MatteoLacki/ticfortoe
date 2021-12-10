#!/usr/bin/env python
import sys
from rq import Connection, Worker
from redis import Redis
import os

testing = os.uname().nodename == "pinguin"
if testing:
    connection = Redis()
else: # must be in the lab
    connection = Redis(
        host='192.168.1.176',
        port=6379, 
    )

with Connection(connection=connection):
    qs = sys.argv[1:] or ['default']
    w = Worker(qs)
    w.work()