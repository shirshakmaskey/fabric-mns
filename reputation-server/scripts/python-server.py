import socket
import threading
import joblib
import json
import os
import memcache
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

HOST = '0.0.0.0'
PORT = 5555
loaded_model = joblib.load("finalized_model.sav")
mc = memcache.Client(['127.0.0.1:11211'], debug=0)
clientArray = {}
ipToNameMap = {
    '192.168.208.15': 'Org1MSP',
    '192.168.208.16': 'Org2MSP',
    '192.168.208.19': 'Org3MSP',
    '192.168.208.17': 'Org4MSP',
    '192.168.208.18': 'Org5MSP'
}
mapChaincodeToNode = {
    '192.168.208.15': '192.168.208.13',
    '192.168.208.16': '192.168.208.10',
    '192.168.208.19': '192.168.208.14',
    '192.168.208.17': '192.168.208.12',
    '192.168.208.18': '192.168.208.11'
}


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
        # response = calculate_reputation(json.loads(msg))
        print("message from client ", json.loads(msg))
        self.localClientSocket.send(bytes(msg, 'UTF-8'))
        self.localClientSocket.close()
        print("Client at ", self.localClientAddress,
              " has successfully disconnected")

    def calculate_reputation(self, data):
        if(data != ''):
            counter = 0
            result = []
            for y in data:
                x = [float(x) for x in data[y]]
                z = [x[0:5]]
                result.append(loaded_model.predict(z)[0])
            json_value = {'Mv1': str(result[0]), 'Mv2': str(
                result[1]), 'Mv3': str(result[2])}
            return json.dumps(json_value)
        else:
            return json.dumps({'Mv1': '', 'Mv2': '', 'Mv3': ''})


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
while True:
    server.listen(6)
    clientsocket, clientAddress = server.accept()
    newthread = reputationClientThread(clientAddress, clientsocket)
    newthread.start()
    for key, value in clientArray.items():
        max_count = max(max_count, value)
        print("max count", max_count, "current value ", value)
        if (max_count-value) > 3:
            clientArray.pop(key)
            GoServerClient(key)
            break
