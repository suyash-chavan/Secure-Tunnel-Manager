from flask import (
    Blueprint,
    make_response,
    request,
    jsonify)

def setCheck(reqJson, *argv):

    missing = []

    for arg in argv:
        if(reqJson[arg] == None):
            missing.append(arg)
    
    if(len(missing)!=0):
        return make_response(jsonify({
            "status": "Missing {}".format(str(missing))
        }), 401)

