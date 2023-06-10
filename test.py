document = {"a": "b", "c": {"d": [{"1": "e"}, {"2": "f"}]}}

# we need output like this
# {"1": "t"}

# case 1:
# data = {"c.d.0.1": "t"}


# for key, value in data.items():
#     keys = key.split(".")
#     temp = document
#     for key in keys[:-1]:
#         # print(
#         #     "key", key, "\nkeytype", type(key), "\ntemp", temp, "\ntemptype", type(temp)
#         # )
#         if key.isdigit() and isinstance(temp, list):
#             temp = temp[int(key)]
#         else:
#             temp = temp.setdefault(key, {})

#     print("parent", temp, "\nkey:", keys[-1], "\nvalue:", value)


# case 2:
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
