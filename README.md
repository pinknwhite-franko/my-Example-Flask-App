# my-Example-Flask-App

my-Example-Flask-App is a simple Flask application template that use flask to run any python script.

## Installation

Use the the following set to download the application on OSX or linux:
Step 1: Download python 3.8 and later

Step 2: download virtualvenv

Step 3: Activte a new venv and download the required packages
```bash
venv\scripts\activate
python -m pip install -r requirements.txt
```

Step 4: download flask
```bash
pip install flask
if not working, try:
    pip install -U pandas
```

Step 5: Download the app
```bash
set FLASK_APP='myApp/app.py'
pip install -e .
```

Step 5: Run the app
```bash
flask run
```

## Usage
head to your localhost url to playround the app

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
