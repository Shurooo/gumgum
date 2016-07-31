import json


var_ = ["cc", "rg", "margin", "tmax", "typeid", "bti", "bidderid", "verticalid", "bidfloor", "format", "product", "cat", "pcat", "domain", "bkc", "hour", "day", "banner"]
dict_all = {}
for i in range(len(var_)):
    var = var_[i]
    dict_all.update({var: ([], [])})
    with open("Play_dict/" + var + ".ods", "r") as file_in:
        dict_var = dict_all[var]
        for line in file_in:
            entry = line.rstrip("\r\n").split(",")
            if var == "banner":
                w = int(entry[0].replace("\"(", ""))
                h = int(entry[1].replace(")\"", ""))
                feature = (w, h)
            elif var == "margin" or var == "bidfloor":
                feature = float(entry[0])
            elif not var in ["cc", "rg", "domain"]:
                if entry[0] == "":
                    feature = -13
                else:
                    feature = int(entry[0])
            else:
                feature = entry[0]
            ratio = float(entry[len(entry)-1])
            dict_var[0].append(feature)
            dict_var[1].append(ratio)

with open("/home/wlu/Desktop/dict_all.json", "w") as file_out:
    json.dump(dict_all, file_out)
