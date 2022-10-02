from flask import Flask, render_template,request, redirect, url_for
from database.DatabaseManager import new_connection, build_database, check_request, remove_invalid_session, new_request
from json import loads

app = Flask("zeon-kyc")
HTML_PATH = "htmls/"

@app.route('/')
def index():
    session, publickey = new_connection(request.remote_addr)
    data = {"session": session, "publickey": publickey}
    return render_template("index.html", data = data)


@app.route("/kycstep1", methods=["GET", "POST"])
def step1():
    data = {}
    if request.method == "POST" and len(request.data) > 0:
        data = loads(request.data)
        session = data["session"]
        publickey = data["publickey"]
        status = check_request(session, publickey)
        if status == -1:
            return "Invalid session ID"
        elif status == 0:
            remove_invalid_session(session)
            return "Either Request Timed out or you are a bot"
        else:
            publickey = new_request(session)
            data = {"session": session, "publickey": publickey}
    if data:
        return render_template("step1KYC.html", data = data)
    else:
        return render_template("step1KYC.html", data = data)

@app.route("/kycstep2", methods=["GET", "POST"])
def step2():
    print("ran")
    if request.method == "POST" and len(request.data.length) >0:
        data = loads(request.data)
        session = data["session"]
        publickey = data["publickey"]
        print(data["name"])
        print(data["dob"])
        status = check_request(session, publickey)
        return render_template("index.html", data = data)
        # if status == -1:
        #     return "Invalid session ID"
        # elif status == 0:
        #     remove_invalid_session(session)
        #     return "Either Request Timed out or you are a bot"
        # else:
        #     publickey = new_request(session)
        #     data = {"session": session, "publickey": publickey}





if __name__ == '__main__':
    build_database()
    app.run(host = "192.168.52.194", port=5000,debug=True)