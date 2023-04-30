from re import match
import asyncio
from .document import Document


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

    all_matched = True

    for key, value in query.items():
        # If there is a dot in the key, it means that we have to go deeper
        if "." in key:
            key, subkey = key.split(".", 1)
            try:
                result = await match_data(data=data[key], query={subkey: value})
                all_matched = all_matched and result
            except:
                continue
        # If the key starts with $, it means that it is an operator
        elif key.startswith("$") and key in query_operators:
            # Check if function is async
            if asyncio.iscoroutinefunction(query_operators[key]):
                # If it is async, we have to await it
                result = await query_operators[key](data, value)
            else:
                # If it is not async, we just call it
                result = query_operators[key](data, value)
            # Update all_matched
            all_matched = all_matched and result
        # If the value is a dict, it means that we have to go deeper
        elif isinstance(value, dict):
            try:
                result = await match_data(data[key], value)
            except:
                result = False
            all_matched = all_matched and result
        else:
            result = data[key] == value
            all_matched = all_matched and result

    return all_matched


async def update_data(document: Document, update: dict) -> Document:
    # Example dict:
    # {
    #     "_id": 1234567890,
    #     "name": "Ashen",
    #     "age": 18,
    #     "friends": ["John", "Jane", "Jack"],
    #     "address": {
    #         "street": {
    #            "housing": 123
    #         },
    #         "number": 123,
    #         "city": "New York",
    #         "country": "USA"
    #     }
    # }
    # Example updates:
    # Update Name : {"$set": {"name": "Ashen Parikh"}}
    # Update Age : {"$inc": {"age": 1}}
    # Update Friends : {"$push": {"friends": ["Joe", "Jill"]}}
    # Update Address : {"$set": {"address.street": "Wall Street"}}
    # Update All: {"$set": {"name": "Ashen Parikh"}, "$inc": {"age": 1}, "$push": {"friends": ["Joe", "Jill"]}, "$set": {"address.street": "Wall Street"}}

    # Algorithm:
    # 1. Check if key starts with $ which means that it is an operator
    # 2. If it is an operator, check if it is a valid operator and proceed accordingly
    # 2.1 If it is a valid operator, get the value which is a dict and proceed accordingly
    # 2.2 The key from the value is our new key and the value from the value is our new value
    # 2.3 If the new key has a dot in it, it means that we have to go deeper
    # 2.4 If the new key does not have a dot in it, it means that we have to update the value
    # 3. If it is not an operator, check if it is a valid key and proceed accordingly
    # 4. If it is not a valid key, raise an error

    update_operators = {
        "$set": lambda x, y: y,
    }

    # document = {
    #     "name": "Ashen",
    #     "address": {
    #         "street": {
    #            "housing": 123
    #         }
    #     }
    # }
    for key, value in update.items():
        # key: $set
        # or value: {"name": "Ashen Parikh"}
        # value: {"address.street.housing": "234"}
        for new_key, new_value in value.items():
            # new_key: name
            # or new_key: address.street.housing

            # new_value: Ashen Parikh
            # or new_value: 234
            keys = new_key.split(".")
            if "." not in new_key:
                new_document = document
            else:
                # new_key: address.street.housing
                # new_value: 234
                # keys: ["address", "street", "housing"]
                new_document = document
                for x in keys[:-1]:
                    # key: address
                    new_document = document[x]

            update_function = update_operators[key]
            updated_document = {keys[-1]: update_function(new_document, new_value)}
            for i in reversed(keys[:-1]):
                updated_document = {i: updated_document}

            await document.update(updated_document)

    return document
