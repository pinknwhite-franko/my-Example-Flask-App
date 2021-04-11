from flask import Flask
app = Flask(__name__)

import app_package.app
import app_package.galab_report_cleanup_v2_weekly_update
import app_package.galab_report_cleanup_v1_quarterly_update