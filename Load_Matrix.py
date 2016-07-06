import os


with open("io_addr_root.txt", "r") as file_addr_root:
    __ADDR_ROOT = file_addr_root.readline().replace("\"", "").rstrip("\n")

list_day = [i for i in range(2,3)]
list_hour = [i for i in range(1)]
list_month = [5]

def make_file_dir():
    list_file_dir = []
    for month in list_month:
        for day in list_day:
            if month == 6:
                day += 18
            for hour in list_hour:
                file_dir = os.path.join(str(month).rjust(2, "0"),
                                        str(day).rjust(2, "0"),
                                        str(hour).rjust(2, "0"))
                list_file_dir.append(file_dir)
    return list_file_dir

list_file_dir = make_file_dir()

X = []
for file_dir in list_file_dir:
    with open(os.path.join(__ADDR_ROOT, file_dir, "output.ods")) as file_in:
        for line in file_in:
            entries = line.rstrip("\r\n").split(",")
            X.append(entries)
