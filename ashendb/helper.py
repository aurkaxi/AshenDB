from re import match
import asyncio, time


from .document import Document


async def match_data(document: Document or dict, query: dict) -> bool:
    async def and_operator(document: Document or dict, queries: list) -> bool:
        pass

    async def or_operator(document: Document or dict, queries: list) -> bool:
        print("Step 3: ", document, queries)
        truth = False
        for qx in queries:
            print("Step 4: ", qx)
            res = await match_query(document, qx)
            truth = truth or res
        return truth

    async def not_operator(document: Document or dict, queries: list) -> bool:
        pass

    async def nor_operator(document: Document or dict, queries: list) -> bool:
        pass

    logical_operators = {
        "$and": and_operator,
        "$or": or_operator,
        "$not": not_operator,
        "$nor": nor_operator,
    }

    # example:
    # json1:
    # {
    #    "name":{"first": "Ashen"},
    #   "age": 20,
    #  "money": 3567
    # }
    # json2:
    # {
    #    "name":{"first": "Ashen"},
    #   "age": 30,
    #  "money": 3567
    # }
    # query 1: {
    #     "$or": [
    #         {"$eq": {"_id": "1f6fc89a-e641-440b-86dc-ece8af75007d"}},
    #         {"$eq": {"name": "abc"}},
    #         {"$eq": {"members.owner": "abc"}},
    #     ]
    # }
    all_true = True
    for q in query:
        print("Step 1: ", q)
        if q not in logical_operators:
            raise Exception(f"Unknown operator {q}")
        print("Step 2: ", query[q])
        res = await logical_operators[q](document, query[q])
        all_true = all_true and res

    return all_true


async def decode_key(document: Document or dict, data: dict) -> tuple:
    """Decode the key

    Args:
        data (dict): The data to decode.
        document (Document): The document to decode.

    Returns:
        tuple(dict, str, Any): Parent Dict, Key, New Value

    Raises:
        Exception: If you try to perform operation on a value.

    Note:
        Keys can't end with [index], because an item inside a list is considered as value, not key. You can't perform operation to a value, but to a dict.

    Example:
        >>> data = {"name.first[0].A": 2}
        >>> document = {"name": {"first": [{"A": 1}]}}
        >>> decode_key(data, document)
        ({"name": {"first": [{"A": 1}]}}, "name.first[0].A", 2)
    """

    temp = document
    keycode = list(data.keys())[0]
    keys = keycode.split(".")
    if "]" in keys[-1]:
        raise Exception("You can't perform operation on a value")
    for key in keys[:-1]:
        if "[" in key:
            kx, ki = key.split("[")
            ki = int(ki[:-1])
            temp = temp[kx][ki]

        else:
            temp = temp.setdefault(key, {})
    return (temp, keys[-1], data[keycode])


async def match_query(document: Document or dict, query: dict) -> bool:
    """Match a document with a query.

    Args:
        data: The document to match.
        query: The query to match with.

    Example:
        >>> await match_data({"name.first": "Ashen"}, {"name.first": "Ashen"})
        True

    Note:
        Keys can't end with [index], because an item inside a list is considered as value, not key. You can't perform operation to a value, but to a dict.
        All the operators might not work. Please report as bug.

        .. list-table::
            :header-rows: 1
            :widths: 20 20 20 20 20 20

            * - Comparison
              - Element
              - Evaluation
              - Geospatial
              - Array
            * - $eq
              - $exists
              - $mod
              - $geoIntersects
              - $all
            * - $ne
              - $type
              - $regex
              - $geoWithin
              - $elemMatch
            * - $gt
              -
              - $text
              - $near
              - $slice
            * - $gte
              -
              - $where
              - $nearSphere
              -
            * - $lt
              - $elemMatch
              -
              -
              -
            * - $lte
              -
              -
              -
              -
            * - $in
              -
              -
              -
              -
            * - $nin
              -
              -
              -
              -

    """

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

    # async def elemMatch_operator(x, y):
    #     for i in x:
    #         if await match_data(i, y):
    #             return True
    #     return False

    array_operators = {
        "$all": lambda x, y: all([i in x for i in y]),
        # "$elemMatch": elemMatch_operator,
        "$size": lambda x, y: len(x) == y,
    }

    query_operators = {
        **comparison_operators,
        **element_operators,
        **evalutation_operators,
        **geospatial_operators,
        **array_operators,
    }

    # example:
    # json1:
    # {
    #    "name.first": "Ashen",
    #   "age": 20,
    #  "money": 3567
    # }
    # json2:
    # {
    #    "name.first": "Ashen",
    #   "age": 30,
    #  "money": 3567
    # }
    # query =  {
    #         "$or": [
    #             {"$eq": {"_id": "1f6fc89a-e641-440b-86dc-ece8af75007d"}},
    #             {"$eq": {"name": "abc"}},
    #             {"$eq": {"members.owner": "abc"}},
    #         ]
    #     }
    result = True
    for operator, data in query.items():
        print("Step 5: ", operator, data)
        if operator not in query_operators:
            raise Exception(f"Unknown operator {operator}")
        for keycode, value in data.items():
            print("Step 6: ", keycode, value)
            parent, key, new_value = await decode_key({keycode: value}, document)
            print("Step 7: ", parent, key, new_value)
            try:
                result = result and query_operators[operator](parent[key], new_value)
                # print(result)
            except KeyError:
                continue
    return result


async def update_data(document: Document or dict, update: dict) -> Document:
    """
    Update a document with the given update query.

    Args:
        document (Document): The document to update.
        update (dict): The update query.

    Example:
        >>> document = {"name.first": "John", "age": 20}
        >>> update = {"$set": {"age": 21}}
        >>> await update_data(document, update)
        {"name.first": "John", "age": 21}

    Note:
        Keys can't end with [index], because an item inside a list is considered as value, not key. You can't perform operation to a value, but to a dict.
        All the operators might not work. Please report as bug.

        .. list-table::
            :header-rows: 1
            :widths: 25 25 25

            * - Field Operators
              - Array Operators
              - Modification Operators
            * - $currentDate ✔
              - $
              - $each
            * - $inc ✔
              - $addToSet ✔
              - $position
            * - $min ✔
              - $pop ✔
              - $slice
            * - $max ✔
              - $pull ✔
              - $sort
            * - $mul ✔
              - $push ✔
              -
            * - $rename.first ✔
              - $pullAll ✔
              -
            * - $set ✔
              -
              -
            * - $setOnInsert ✔
              -
              -
            * - $unset ✔
              -
              -
    """
    field_operators = {
        "$currentDate": lambda parent_key, key, value: parent_key.__setitem__(
            key, int(time.time())
        )
        or parent_key,
        "$inc": lambda parent_key, key, value: parent_key.__setitem__(
            key, parent_key[key] + value
        )
        or parent_key,
        "$min": lambda parent_key, key, value: parent_key.__setitem__(
            key, min(value, parent_key.get(key, float("inf")))
        )
        or parent_key,
        "$max": lambda parent_key, key, value: parent_key.__setitem__(
            key, max(value, parent_key.get(key, float("-inf")))
        )
        or parent_key,
        "$mul": lambda parent_key, key, value: parent_key.__setitem__(
            key, parent_key[key] * value
        )
        or parent_key,
        "$rename.first": lambda parent_key, key, value: parent_key.__setitem__(
            value, parent_key.pop(key)
        )
        or parent_key,
        "$set": lambda parent_key, key, value: parent_key.__setitem__(key, value)
        or parent_key,
        # setOnInsert inserts the value only if that didn't exist before
        "$setOnInsert": lambda parent_key, key, value: parent_key.__setitem__(
            key, value
        )
        if key not in parent_key
        else parent_key,
        "$unset": lambda parent_key, key, value: parent_key.__delitem__(key)
        if key in parent_key
        else None,
    }
    array_operators = {
        # "$" Acts as a placeholder to update the first element that matches the query condition.
        "$": lambda parent_key, key, query, update: "THIS IS NOT IMPLEMENTED YET",
        "$[]": lambda parent_key, key, query, update: "THIS IS NOT IMPLEMENTED YET",
        "$[<identifier>]": lambda parent_key, key, query, update: "THIS IS NOT IMPLEMENTED YET",
        "$addToSet": lambda parent_key, key, value: parent_key.__setitem__(
            key, parent_key[key] + [value]
        )
        if value not in parent_key[key]
        else parent_key,
        "$pop": lambda parent_key, key, value: parent_key.__setitem__(
            key, parent_key[key][:-1]
        )
        if value == -1
        else parent_key.__setitem__(key, parent_key[key][1:])
        if value == 1
        else parent_key,
        "$pull": lambda parent_key, key, value: parent_key.__setitem__(
            key,
            [
                item
                for item in parent_key[key]
                if not (
                    isinstance(item, dict)
                    and all(k in item and item[k] == v for k, v in value.items())
                )
            ],
        )
        if isinstance(value, dict)
        else parent_key.__setitem__(
            key,
            [item for item in parent_key[key] if item not in value],
        ),
        "$push": lambda parent_key, key, value: parent_key.__setitem__(
            key, parent_key[key].extend(value)
        )
        if key in parent_key and hasattr(value, "__iter__")
        else parent_key.__setitem__(key, value if isinstance(value, list) else [value]),
        "$pullAll": lambda parent_key, key, value: parent_key.__setitem__(
            key, [item for item in parent_key[key] if item not in value]
        )
        if isinstance(value, list)
        else parent_key,
    }

    modification_operators = {
        "$each": lambda x, y: y,
        "$position": lambda x, y: y,
        "$slice": lambda x, y: y,
        "$sort": lambda x, y: y,
    }

    update_operators = {
        **field_operators,
        **array_operators,
        **modification_operators,
    }

    for operator, data in update.items():
        for keycode, value in data.items():
            parent, key, new_value = await decode_key(document, {keycode: value})

            if operator in update_operators:
                update_operators[operator](parent, key, new_value)

    await document.save()
    return document
