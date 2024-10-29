from flask import Flask
from swagger_service.routes.swagger_routes import register_swagger_blueprint

app = Flask(__name__)

register_swagger_blueprint(app)

if __name__ == '__main__':
    # http://127.0.0.1:5000/swagger/
    app.run(host="127.0.0.1", port=5000, debug=True)
