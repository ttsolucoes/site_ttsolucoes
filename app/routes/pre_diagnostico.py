from app import app
from config import secret_key
from flask import render_template, request, session, jsonify

app.secret_key = secret_key

@app.route('/pre_diagnostico')
def pre_diagnostico():
    return render_template('pages/public/pre_diagnostico.html')
