from website import create_app
from flask import Flask
if __name__ == "__main__":
    app = create_app()
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.run(debug=True)