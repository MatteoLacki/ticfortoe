def batch_iter(iterables, batch_size=10):
    batch = []
    for el in iterables:
        batch.append(el)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if len(batch):
        yield batch
