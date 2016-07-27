import operator
import csv
import os


def get_result(result_list, feature):
    dict_result = {}
    for result in result_list:
        for key in result:
            if dict_result.has_key(key):
                dict_result[key] += result[key]
            else:
                dict_result.update({key:result[key]})

    print "{} unique {} recorded".format(len(dict_result), feature)
    sorted_result = sorted(dict_result.items(), key=operator.itemgetter(1), reverse=True)
    with open(os.path.join("/home/ubuntu/Weiyi", feature + ".ods"), "w") as file_out:
        wr = csv.writer(file_out)
        for item in sorted_result:
            wr.writerow(item)
