from flask import Flask

app = Flask(__name__)

# Import your views here
from quiz import views

if __name__ == '__main__':
    app.run(debug=True)
