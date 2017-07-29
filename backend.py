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
sockets = []
connectionDict = {}
context = zmq.Context()
weight_list = []
cost_value_list = []

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
            s.bind("tcp://"+str(iplist[index])+":"+portnumber)
            sockets.insert(index*2,s)
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
        s.connect("tcp://"+str(iplist[index])+":"+portnumber)
        sockets.insert(index*2+1,s)
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

@app.route("/run_alg", methods=['POST'])
def run_alg():
    mu = float(request.json['mu'])
    max_ite = int(request.json['max_ite'])
    method = request.json['method']
    start_ite = int(request.json['ite'])
    dist_style = request.json['dist_style']
    iter_per_call = int(request.json['iter_per_call'])
    print ("data received")
    while (start_ite < max_ite):
        if start_ite == 0:
            vr_alg = ZMQ_VR_agent(X,Y, np.random.randn(28*28*10,1), soft_max, socket=sockets, rho = 1e-4, weights = weight_list)
        vr_alg.adapt(mu, start_ite, method, dist_style)
        vr_alg.correct(start_ite, dist_style)
        vr_alg.combine(start_ite, dist_style)

        cost_value = vr_alg.cost_model.func_value()
        cost_value_list.append(cost_value)
        start_ite = start_ite + iter_per_call
    plt.plot(cost_value_list)
    plt.show()

    plt.plot(vr_alg.cost_model.w)
    plt.show()
    return Response(None)


if __name__ == '__main__':
    app.run(host='192.168.1.134', debug=False, port = sys.argv[1])

    