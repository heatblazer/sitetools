#py.exe snooprdr.py mysnoop.snoop
from Utils import *


def main():
    snoop = "C:\\Users\\izapryanov.VERINT\\Desktop\\Captures\\sqrlbug.pcap"
    my_str_as_bytes = str.encode("¼Ó")
    print(my_str_as_bytes)
    Utils.parse_snoop(snoop, my_str_as_bytes)



if __name__ == "__main__":
    main()