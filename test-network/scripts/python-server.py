import socket
import threading
import joblib
import json
import os
import memcache
import calendar
import time
import warnings
from collections import OrderedDict
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

HOST = '0.0.0.0'
PORT = 5555
loaded_model = joblib.load("finalized_model.sav")
mc = memcache.Client(['127.0.0.1:11211'], debug=0)
clientArray = {}
ipToNameMap = {
    '192.168.240.16': 'Org1MSP',
    '192.168.240.17': 'Org2MSP',
    '192.168.240.15': 'Org3MSP',
    '192.168.240.18': 'Org4MSP',
    '192.168.240.19': 'Org5MSP'
}
mapChaincodeToNode = {
    '192.168.240.16': '192.168.240.12',
    '192.168.240.17': '192.168.240.14',
    '192.168.240.15': '192.168.240.11',
    '192.168.240.18': '192.168.240.10',
    '192.168.240.19': '192.168.240.13'
}
mc.set("addedBlock", 0, 7200)
flag = OrderedDict()


class reputationClientThread(threading.Thread):
    def __init__(self, clientAddress, clientSocket):
        threading.Thread.__init__(self)
        self.localClientSocket = clientSocket
        self.localClientAddress = clientAddress
        print("New connection has been added from: ", self.localClientAddress)
        # print("host name of connection", self.localClientAddress[0])
        if not mc.get(self.localClientAddress[0]):
            # print("going in if loop")
            mc.set(self.localClientAddress[0], 1, 7200)
            mc.set(self.localClientAddress[0] +
                   ":age", calendar.timegm(time.gmtime), 7200)
            local_dict = {self.localClientAddress[0]: mc.get(
                self.localClientAddress[0])}
            clientArray.update(local_dict)
            print("1#", clientArray.items())

        else:
            print(mc.get(self.localClientAddress[0]))
            print("going in else loop")
            mc.incr(self.localClientAddress[0])
            clientArray[self.localClientAddress[0]] = mc.get(
                self.localClientAddress[0])

    def run(self):
        print("Calculating the reputation value for ", self.localClientAddress)
        data = self.localClientSocket.recv(1024)
        print(data)
        msg = data.decode()
        flag[msg][self.localClientAddress[0]] = 1
        if len(flag) > 1:
            for ip in flag[-2]:
                for clientIp in ipToNameMap:
                    if not clientIp in ip:
                        if not mc.get(clientIp+":flag"):
                            mc.set(clientIp+":flag", 1, 7200)
                        mc.incr(clientIp)

        print("message from client ", json.loads(msg))
        self.localClientSocket.send(bytes(msg, 'UTF-8'))
        self.localClientSocket.close()
        print("Client at ", self.localClientAddress,
              " has successfully disconnected")


def calculate_reputation(self, keyValue):
    if(key != ''):
        counter = 0
        result = 5

        input = []
        input.append(calendar.timegm(time.gmtime)-mc.get(key+":age"))
        input.append(mc.get(key))
        input.append(mc.get(mc.get("addedBlock")))
        input.append(mc.get(key+":flag"))
        input.append(mc.get(key+":flag")/mc.get("addedBlock"))
        x = [float(x) for x in input]
        result = loaded_model.predict(x)[0]
        if int(result) < 5:
            return True
        else:
            return False
    else:
        return False


def GoServerClient(peerName):
    mycount = 1
    for key in clientArray:
        if(mycount < len(clientArray)):
            send_data = json.dumps(
                {"PeerNode": ipToNameMap[peerName], "Action": "delete", "Final": 0})
        else:
            send_data = json.dumps(
                {"PeerNode": ipToNameMap[peerName], "Action": "delete", "Final": 1})
        print(send_data)
        print("this is connect ip", mapChaincodeToNode[key])
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((mapChaincodeToNode[key], 6666))
        client.sendall(bytes(send_data, "UTF-8"))
        client.close()
        mycount += 1

    f = open("orgSelector.txt", "w+")
    f.write(send_data)
    f.close()
    print("testing go server")


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((HOST, PORT))
print("Server started")
print("Waiting for client request..")

max_count = 0
min_count = 100000
while True:
    server.listen(6)
    clientsocket, clientAddress = server.accept()
    newthread = reputationClientThread(clientAddress, clientsocket)
    newthread.start()
    for key, value in clientArray.items():
        min_count = min(min_count, value)
        mc.replace("addedBlock", min_count)
        max_count = max(max_count, value)
        print("max count", max_count, "current value ", value)
        if calculate_reputation(key):
            clientArray.pop(key)
            GoServerClient(key)
            break
