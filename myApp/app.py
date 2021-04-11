from flask import Flask
from flask import redirect
from flask import request
from flask import jsonify
from flask import render_template
from flask import Flask, send_from_directory
from myApp import app
from myApp import my_python_script
import time

submitButtonTextInitial = "Run python script"


@app.route("/static")
def static_dir(path):
    return send_from_directory("static")

# the route() decorator to tell Flask what URL should trigger our function.


@app.route('/')
def hello_world():
    return render_template('home.html',title="Home")

# def is_relative(url_link):
#   return re.match(r"^\/[^\/\\]", url_link)

@app.route('/page1', methods=['GET'])
def weekly_page():
    return render_template('page1.html',title="page1", submitButtonText=submitButtonTextInitial)


@app.route('/runPython', methods=['GET','POST'])
def copy_orin_files_w():
    if request.method == "GET":
        try:
            my_python_script.main()
            return 'Python scripted Ran', 200
        except:
            return 'Error from the backend', 500
