from flask import Flask, request, jsonify
from models.user import User
from database import db
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:admin123@127.0.0.1:3306/flask-auth-crud"

login_manager = LoginManager()

db.init_app(app)
login_manager.init_app(app)

# Login View
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(user_id)

@app.route("/login", methods=["POST"])
def login():
  data = request.json
  username = data.get("username")
  password = data.get("password")

  if username and password:
    # Login
    user = User.query.filter_by(username=username).first()

    if user and user.password == password:
      login_user(user)
      return jsonify({"message": "Successfully authenticated"})

  return jsonify({"message": "Invalid credentials"}), 400

@app.route("/logout", methods=["GET"])
@login_required
def logout():
  logout_user()
  return jsonify({"message": "Successfully logged out"})

@app.route("/user", methods=["POST"])
def create_user():
  data = request.json
  username = data.get("username")
  password = data.get("password")

  if username and password:
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User successfully created"})

  return jsonify({"message": "Invalid credentials"}), 400

@app.route("/user/<int:id_user>", methods=["GET"])
@login_required
def read_user(id_user):
  user = User.query.get(id_user)

  if user:
    return {"username": user.username}

  return jsonify({"message": "User not found"}), 404

@app.route("/user/<int:id_user>", methods=["PUT"])
@login_required
def update_user(id_user):
  data = request.json
  new_password = data.get("password")
  user = User.query.get(id_user)

  if user and new_password:
    user.password = new_password
    db.session.commit()
    return jsonify({"message": f"User {id_user} successfully updated"})

  return jsonify({"message": "User not found"}), 404

@app.route("/user/<int:id_user>", methods=["DELETE"])
@login_required
def delete_user(id_user):
  user = User.query.get(id_user)

  if current_user.id == id_user:
    return jsonify({"message": "You are not allowed to delete yourself"}), 403

  if user:
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"User {id_user} successfully deleted"})

  return jsonify({"message": "User not found"}), 404


if __name__ == "__main__":
  app.run(debug=True)
