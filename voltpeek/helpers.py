def map_many(functions, iterable):
    return reduce(lambda x, y: map(y, x), *functions, iterable)
