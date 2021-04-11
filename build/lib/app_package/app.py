from flask import Flask
from flask import redirect
from flask import request
from flask import jsonify
from flask import render_template
from flask import Flask, send_from_directory
from app_package import app
from app_package import galab_report_cleanup_v2_weekly_update
import time
import re

submitButtonTextInitial = "Run python script"
submitButtonTextSuccess = "script ran successfully, rerun"
submitButtonTextFail = "script failed"


@app.route("/static")
def static_dir(path):
    return send_from_directory("static")

# the route() decorator to tell Flask what URL should trigger our function.


@app.route('/')
def hello_world():
    return render_template('home.html', title='Welcome', weeklysubmitButtonText=submitButtonTextInitial)
    # return render_template('success.html',type="Weekly")

# def is_relative(url_link):
#   return re.match(r"^\/[^\/\\]", url_link)


@app.route('/success')
def success_page():
    return render_template('success.html', type="Weekly")


@app.route('/weekly_cleanup', methods=['GET'])
def run_weekly_clean():
    if request.method == "GET":
        try:
            # galab_report_cleanup_v2_weekly_update.main()
            return redirect('/success')
        except ValueError:
            return render_template('home.html', weeklysubmitButtonText=submitButtonTextFail)


@app.route('/quarterly_cleanup', methods=['GET', 'POST'])
def quarterly_clean():
    '''execute whatever code you want when the button gets clicked here'''
    # galab_report_cleanup_v1_quarterly_update.main()
    return render_template('home.html')
