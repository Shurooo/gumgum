import json
import csv
import operator


result_list = []


def get_dates():
    may = [(5, i, j) for i in range(1, 8) for j in range(24)]
    # may = []
    # june = [(6, i, j) for i in range(4, 26) for j in range(24)]
    june = []
    return may+june


def run(addr_in):
    dict_domain = {}
    with open(addr_in, "r") as file_in:
        for line in file_in:
            entry = json.loads(line)
            domain = (entry["auction"]["site"]["domain"])
            if (domain == None) or (len(domain) == 0):
                domain = "NONE"
            domain_tmp = domain.split("www.")
            domain = domain_tmp[len(domain_tmp)-1]
            if dict_domain.has_key(domain):
                dict_domain[domain] += 1
            else:
                dict_domain.update({domain:1})
    return dict_domain


def add_result(result):
    result_list.append(result)


def get_result():
    dict_domain = {}
    for result in result_list:
        for key in result:
            if dict_domain.has_key(key):
                dict_domain[key] += result[key]
            else:
                dict_domain.update({key:result[key]})

    print "{} unique domains recorded".format(len(dict_domain))
    sorted_domain = sorted(dict_domain.items(), key=operator.itemgetter(1), reverse=True)
    with open("/home/ubuntu/Weiyi/domains.ods", "w") as file_out:
        wr = csv.writer(file_out)
        for item in sorted_domain:
            wr.writerow(item)
