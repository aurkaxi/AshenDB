from re import match
import asyncio


async def match_data(data: dict, query: dict) -> bool:
    comparison_operators = {
        "$eq": lambda x, y: x == y,
        "$ne": lambda x, y: x != y,
        "$gt": lambda x, y: x > y,
        "$gte": lambda x, y: x >= y,
        "$lt": lambda x, y: x < y,
        "$lte": lambda x, y: x <= y,
        "$in": lambda x, y: x in y,
        "$nin": lambda x, y: x not in y,
    }

    async def and_operator(x, y):
        for i in y:
            if not await match_data(x, i):
                return False
        return True

    async def or_operator(x, y):
        for i in y:
            if await match_data(x, i):
                return True
        return False

    async def not_operator(x, y):
        return not await match_data(x, y)

    async def nor_operator(x, y):
        for i in y:
            if await match_data(x, i):
                return False
        return True

    logical_operators = {
        "$and": and_operator,
        "$or": or_operator,
        "$not": not_operator,
        "$nor": nor_operator,
    }

    element_operators = {
        "$exists": lambda x, y: y in x,
        "$type": lambda x, y: type(x) == y,
    }
    evalutation_operators = {
        "$mod": lambda x, y: x % y[0] == y[1],
        "$regex": lambda x, y: y.match(x),
        "$text": lambda x, y: y in x,
        "$where": lambda x, y: y(x),
    }
    geospatial_operators = {
        "$geoIntersects": lambda x, y: x in y,
        "$geoWithin": lambda x, y: x in y,
        "$near": lambda x, y: x in y,
        "$nearSphere": lambda x, y: x in y,
    }

    async def elemMatch_operator(x, y):
        for i in x:
            if await match_data(i, y):
                return True
        return False

    array_operators = {
        "$all": lambda x, y: all([i in x for i in y]),
        "$elemMatch": elemMatch_operator,
        "$size": lambda x, y: len(x) == y,
    }
    projection_operators = {
        "$": lambda x, y: x,
        "$elemMatch": lambda x, y: x,
        "$meta": lambda x, y: x,
        "$slice": lambda x, y: x,
    }

    query_operators = {
        **comparison_operators,
        **logical_operators,
        **element_operators,
        **evalutation_operators,
        **geospatial_operators,
        **array_operators,
        **projection_operators,
    }

    for key, value in query.items():
        # If there is a dot in the key, it means that we have to go deeper
        if "." in key:
            key, subkey = key.split(".", 1)
            # try:
            return await match_data(data=data[key], query={subkey: value})
            # except:
            #     print("error")
            #     continue
        # If the key starts with $, it means that it is an operator
        elif key.startswith("$") and key in query_operators:
            # Check if function is async
            if asyncio.iscoroutinefunction(query_operators[key]):
                # If it is async, we have to await it
                return await query_operators[key](data, value)
            else:
                # If it is not async, we just call it
                return query_operators[key](data, value)
        # If the value is a dict, it means that we have to go deeper
        elif isinstance(value, dict):
            try:
                return await match_data(data[key], value)
            except:
                continue
        return data[key] == value
