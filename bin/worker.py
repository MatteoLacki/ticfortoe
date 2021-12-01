#!/usr/bin/env python
import sys
from rq import Connection, Worker
from redis import Redis

with Connection(
    connection=Redis(
        host='192.168.1.176',
        port=6379,
    )
):
    qs = sys.argv[1:] or ['default']
    w = Worker(qs)
    w.work()