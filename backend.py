from flask import Flask, render_template, jsonify, request, Response
app = Flask(__name__)

import numpy as np
import matplotlib.pyplot as pyplot
import os, sys
from util.read_data import *
from util.VR_algorithm import *
from util.cost_func import soft_max
from scipy.misc import imresize
import zmq
import json


iplist = []
socketsBind = []
socketsConnect = []
sockets = []
connectionDict = {}
context = zmq.Context()
weight_list = []

@app.route("/", methods=['GET'])
def index():
    return render_template("index.html")

@app.route("/sendIP", methods=['POST'])
def sendIP():
    retrievedIP = request.json['sentIP']
    if retrievedIP not in iplist:
        iplist.append(retrievedIP)
        print ("Added IP.")
    else:
        print ("Already in list.")
    return jsonify({'iplist': iplist})

@app.route("/bind", methods=['POST'])
def bind():
    index = int(request.json['index'])
    if iplist[index] in connectionDict:
        return Response(None)
    else:
        try:
            portnumber = 9999 - index
            connectionDict.update({iplist[index]: str(portnumber)})
            s = context.socket(zmq.PAIR)
            s.bind("tcp://"+str(iplist[index])+":"+connectionDict[iplist[index]])
            socketsBind.insert(index,s)
            sockets = socketsBind + socketsConnect
            return Response(None)
        except:
            print('Already Bound.')
            return Response(None)

@app.route("/connect", methods=['POST'])
def connect():
    index = int(request.json['index'])
    try:
        portnumber = 9999 - index
        s = context.socket(zmq.PAIR)
        s.connect("tcp://"+str(iplist[index])+":"+connectionDict[iplist[index]])
        socketsConnect.insert(index,s)
        sockets = socketsBind + socketsConnect
        return Response(None)
    except:
        print ('Connected to another computer')
        return Response(None)

@app.route("/generateWeights", methods=['GET'])
def generateWeights():
    weight_list = []
    self_nbrNum = len(sockets) + 1
    for s in sockets:
        s.send_json(self_nbrNum)
    
    for s in sockets:
        nbr_nbrNum = s.recv_json()
        weight_list.append(1/max(self_nbrNum, nbr_nbrNum))

    self_weight = 1 - sum(weight_list)
    weight_list.insert(0, self_weight)
    print (weight_list)
    return Response(None)

@app.route("/get_data", methods=['POST'])
def get_data():
    tmp_mask=request.json['mask']
    mask = [int(i) for i in tmp_mask if tmp_mask[i]]

    global vr_alg, X, Y
    X,Y = read_mnist (datatype='multiclass', mask_label=mask)
    X = X[:int(X.shape[0]*0.2)]
    Y = Y[:int(Y.shape[0]*0.2)]
    
    return Response(None)



if __name__ == '__main__':
    app.run(debug=False, port = sys.argv[1])

    