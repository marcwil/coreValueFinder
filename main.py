#!/usr/bin/python3
from random import choice
import os
import sys
import operator
import json
import time
import glob


class Graph(object):
    def __init__(self, n):
        self._adj = [0] * n
        for i in range(n):
            self._adj[i] = [0]*n

    @property
    def adj(self):
        return self._adj

    def add_edge(self, u, v):
        self._adj[u][v] += 1
    

def loadValues():
    valuesFiles = glob.glob('*.values')
    selection = 0
    if (len(valuesFiles) > 1):
        print("Present value sets:")
        for i, path in enumerate(valuesFiles):
            print("[{}] {}".format(i+1, path))
        selection = int(input("Load value set: "))
    try:
        with open(valuesFiles[selection-1]) as json_file:
            return json.load(json_file)
    except Exception as e:
        print(f"Failed loading value set: {str(e)}")
        return {}

def getSessionFilePath():
    sessions = glob.glob('.*.session')
    print("Present Sessions:")
    print("[0] New Session")
    for i, path in enumerate(sessions):
        print(f"[{i+1}] {path}")

    inp = input("Load Session: ")
    if (inp == "" or inp == "0"):
        return None
    return sessions[int(inp)-1]


def clear(text=""):
    # for linux and mac
    if os.name == "posix":
        _ = os.system("clear")

    # for windows (here, os.name is 'nt')
    else:
        _ = os.system("cls")

    if text:
        print(text)

def get_input(min_value, max_value) -> int:
    """ Returns a number, if one got 'inputted'.
    Might throw a KeyboardInterrupt.

    Args:
        min_value: lower bound
        max_value: upper bound

    Returns:
        int: number between min_value and max_value inclusive

    Throws:
        KeyboardInterrupt, if the user intends to end inputting values
    """
    try:
        inp = input()
    except EOFError:
        raise KeyboardInterrupt("exiting")

    lower = inp.lower()
    if lower == "exit" or lower == "end" or not lower:
        raise KeyboardInterrupt("exiting")

    try:
        index = int(inp)
        assert index >= min_value
        assert index <= max_value
    except (ValueError, AssertionError):
        print(
            "Please enter '1', '2' or '3' to select one of the presented values, or '0' if they are of equal value to you."
        )
        return get_input(min_value, max_value)  # this might lead to a very unlikely
        # 'recursion limit error' when repeated more than 5k times.
    return index

def main(showDescr = True):
    print("welcome to the core value finder")
    values = {}
    valueset = loadValues()

    sessionPath = getSessionFilePath()
    try:
        with open(sessionPath) as json_file:
            data = json.load(json_file)
            values = data['values']
    except Exception as e:
        print(f"Failed loading Session: {str(e)}")
        print("Fallback to new Session")
        sessionPath = None

    if not sessionPath:
        sessionPath = ".{}.session".format(time.strftime("%Y-%m-%d-%H:%M"))
        print("New Session: {}".format(sessionPath))
        for v in valueset.keys():
            values[v] = 0

    for _ in range(len(values) ** 2):
        #select shown values
        selection = []
        for _ in range(0,3):
            while len(values) > len(selection):
                newValue = choice([*values])
                if newValue not in selection:
                    selection += [newValue]
                    break
        clear()
        if showDescr:
            for i in range(0, len(selection)):
                valueName = selection[i]
                desc = valueset.get(valueName, {}).get('descr', "")
                print(f"[{i+1}] {valueName} -- {desc}")
        else:
            print(f"[1] {selection[0]} [2] {selection[1]} [3] {selection[2]}")

        try:
            index = get_input(1, len(selection))
            if index:  # if index == 0: don't evaluate
                values[selection[index - 1]] += 1
        except KeyboardInterrupt:

            print(f"Saving Session: {sessionPath}")
            dump = {
                "values": values,
                "timestamp": time.strftime("%Y%m%d-%H%M%S")
            }
            json_data = json.dumps(dump, indent=2)
            with open(sessionPath,'w') as file:
                file.write(json_data)
            break

    sorted_x = sorted(values.items(), key=operator.itemgetter(1), reverse=True)
    clear("Values sorted by number of times they 'outcompeted' others.")
    print(f"A total of {sum(values.values())} comparisons has been done.\n")
    print("----- ---------------")
    for k, v in sorted_x:
        print(f"{v:>4}: {k}".format(k, v))


if __name__ == "__main__":
    main(not (len(sys.argv) > 1 and sys.argv[1] == "--no-descr"))

