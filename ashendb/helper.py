from re import match
import asyncio, time


from .document import Document


async def match_data(data: Document or dict, query: dict) -> bool:
    """Match a document with a query.

    Args:
        data: The document to match.
        query: The query to match with.

    Example:
        >>> await match_data({"name": "Ashen"}, {"name": "Ashen"})
        True

    Note:
        All the operators might not work. Please report as bug.

        .. list-table::
            :header-rows: 1
            :widths: 20 20 20 20 20 20

            * - Comparison
              - Logical
              - Element
              - Evaluation
              - Geospatial
              - Array
            * - $eq
              - $and
              - $exists
              - $mod
              - $geoIntersects
              - $all
            * - $ne
              - $or
              - $type
              - $regex
              - $geoWithin
              - $elemMatch
            * - $gt
              - $not
              -
              - $text
              - $near
              - $slice
            * - $gte
              - $nor
              -
              - $where
              - $nearSphere
              -
            * - $lt
              - $elemMatch
              -
              -
              -
              -
            * - $lte
              -
              -
              -
              -
              -
            * - $in
              -
              -
              -
              -
              -
            * - $nin
              -
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

    query_operators = {
        **comparison_operators,
        **logical_operators,
        **element_operators,
        **evalutation_operators,
        **geospatial_operators,
        **array_operators,
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


async def update_data(document: Document or dict, update: dict) -> Document:
    """
    Update a document with the given update query.

    Args:
        document (Document): The document to update.
        update (dict): The update query.

    Example:
        >>> document = {"name": "John", "age": 20}
        >>> update = {"$set": {"age": 21}}
        >>> await update_data(document, update)
        {"name": "John", "age": 21}

    Note:
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
            * - $rename ✔
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
        "$rename": lambda parent_key, key, value: parent_key.__setitem__(
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
        for key, value in data.items():
            temp = document
            keys = key.split(".")
            for key in keys[:-1]:
                if "[" in key:
                    key, index = key.split("[")
                    index = int(index[:-1])
                    temp = temp[key][index]
                else:
                    temp = temp.setdefault(key, {})

            if operator in update_operators:
                update_operators[operator](temp, keys[-1], value)

    await document.save()
    return document
