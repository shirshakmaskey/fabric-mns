import json
import time
import subprocess
import os
from csv import reader


jsonData = {"A": "1", "B": "2", "C": "3", "D": "4", "E": "5"}


def scriptFunction():
    global jsonData
    # run the script here
    with open('./DACTStrictDataset.csv', 'r') as read_obj:
        csv_reader = reader(read_obj)
        header = next(csv_reader)
        count = 0
        if header != None:
            for row in csv_reader:
                if os.path.exists("./scripts/orgSelector.txt"):
                    f = open("./scripts/orgSelector.txt", "r")
                    myJson = json.loads(f.readline())
                    if myJson['PeerNode'] == "Org5MSP":
                        jsonData["E"] = "0"
                    elif myJson["PeerNode"] == "Org4MSP":
                        jsonData["D"] = "0"
                    f.close()
                command = ['/bin/bash', 'runCC.sh',
                           str(row[0]), str(row[1]), str(row[2]).replace(' ', '-'), str(row[3]), str(row[4]), str(row[5]), str(row[6]), str(row[7]), str(row[8]), str(row[9]), str(row[10]), jsonData["A"], jsonData['B'], jsonData['C'], jsonData['D'], jsonData['E']]
                if count < 2:
                    process = subprocess.Popen(command,
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE)
                    stdout, stderr = process.communicate()
                    print(stdout.decode())
                    print(stderr.decode())
                    # time.sleep(0.02)
                    count += 1
                else:
                    print(count)
                    break
                # time.sleep(5)


scriptFunction()
