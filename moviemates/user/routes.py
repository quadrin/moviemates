from flask import Flask 
from app import app #imports app instance from models.py
from user.models import User

@app.route('/user/signup', methods=['POST'])
def signup():
	return User().signup()

