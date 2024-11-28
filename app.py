from flask import Flask , render_template
from flask import Flask, jsonify

from flask_sqlalchemy import SQLAlchemy
#from flask_swagger import swagger


from flask_wtf.csrf import CSRFProtect




app = Flask(__name__)
#app.secret_key = 'jatinisgood'  # Necessary for CSRF protection
#csrf = CSRFProtect(app)

import config
# Initialize the SQLAlchemy instance and bind it to the app
db = SQLAlchemy()
db.init_app(app)  # This links SQLAlchemy to the app instance



import models
import utils

import routes




#models.reset_database
utils.reset_database()
# Initialize the database
utils.initialize_db()

if __name__ == '__main__':
    app.run(debug=True)

