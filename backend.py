from flask import Flask, render_template, jsonify, request, Response
app = Flask(__name__)


import os, sys

iplist = []

@app.route("/", methods=['GET'])
def index():
    return render_template("index.html")

@app.route("/sendIP", methods=['POST'])
def sendIP():
    retrievedIP = request.json['sentIP']
    if retrievedIP not in iplist:
        iplist.append(retrievedIP)
    print ("Success!")
    return Response(None)



if __name__ == '__main__':
    app.run(debug=False, port = sys.argv[1])

    