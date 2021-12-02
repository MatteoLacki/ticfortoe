from rq.registry import (
    StartedJobRegistry,
    FinishedJobRegistry,
    FailedJobRegistry
)

registry = FailedJobRegistry(
    name='ticfortoe', 
    connection=connection
)
registry.count