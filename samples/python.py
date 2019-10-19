#!/usr/bin/env python3

def main():
    lst = ["2", "0", "1", "9"]
    result = [int(s) for s in lst]
    for n in result:
        print(n, end="")
    #
    print()

##############################################################################

if __name__ == "__main__":
    main()
