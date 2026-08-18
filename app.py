import os

from flask import Flask

import db

app = Flask(__name__)
app.config["DATABASE"] = os.path.join(app.instance_path, "zdravje.db")
os.makedirs(app.instance_path, exist_ok=True)
db.init_app(app)


@app.route("/")
def domov():
    return ""


if __name__ == "__main__":
    app.run(debug=True)
