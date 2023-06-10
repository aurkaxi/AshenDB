document = {"a": "b", "c": {"d": [{"1": "e"}, {"2": "f"}]}}

data = {"c.d[0].1": "t"}

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
    print("parent", temp, "\nkey:", keys[-1], "\nvalue:", value)
