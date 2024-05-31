# import de flask
from flask import Flask
# je fais un include d'un fichier extension
from extensions import jwt
# second include d'un fichier routes
from routes.auth import auth_blueprint
from routes.info_wifi import info_wifi_blueprint

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'secret'

jwt.init_app(app)

app.register_blueprint(auth_blueprint)
app.register_blueprint(info_wifi_blueprint)

if __name__ == '__main__':
    app.run(debug=True)
