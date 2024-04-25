from flask import jsonify
from marshmallow.exceptions import ValidationError
import requests
from core import app
from core.apis.assignments import student_assignments_resources, teacher_assignments_resources
from core.libs import helpers
from core.libs.exceptions import FyleError
from werkzeug.exceptions import HTTPException

from sqlalchemy.exc import IntegrityError

app.register_blueprint(student_assignments_resources, url_prefix='/student')
app.register_blueprint(teacher_assignments_resources, url_prefix='/teacher')


@app.route('/')
def ready():
    response = jsonify({
        'status': 'ready',
        'time': helpers.get_utc_now()
    })

    return response


@app.route('/principal/assignments', methods=['GET'])
def get_principal_assignments():
    principal_id = requests.headers.get('X-Principal', None)
    if principal_id:
        # Logic to fetch assignments based on principal ID
        principal_assignments = [assignment for assignment in assignments]
        return jsonify({"data": principal_assignments}), 200
    else:
        return jsonify({"message": "Principal ID not provided"}), 400

@app.route('/principal/teachers', methods=['GET'])
def get_principal_teachers():
    principal_id = requests.headers.get('X-Principal', None)
    if principal_id:
        # Logic to fetch teachers based on principal ID
        principal_teachers = [teacher for teacher in teachers]
        return jsonify({"data": principal_teachers}), 200
    else:
        return jsonify({"message": "Principal ID not provided"}), 400

@app.route('/principal/assignments/grade', methods=['POST'])
def grade_assignment():
    principal_id = requests.headers.get('X-Principal', None)
    if principal_id:
        data = requests.json
        assignment_id = data.get('id')
        grade = data.get('grade')
        # Logic to grade or re-grade an assignment
        for assignment in assignments:
            if assignment['id'] == assignment_id:
                assignment['grade'] = grade
                assignment['state'] = 'GRADED'
                return jsonify({"data": assignment}), 200
        return jsonify({"message": "Assignment not found"}), 404
    else:
        return jsonify({"message": "Principal ID not provided"}), 400

@app.errorhandler(Exception)
def handle_error(err):
    if isinstance(err, FyleError):
        return jsonify(
            error=err.__class__.__name__, message=err.message
        ), err.status_code
    elif isinstance(err, ValidationError):
        return jsonify(
            error=err.__class__.__name__, message=err.messages
        ), 400
    elif isinstance(err, IntegrityError):
        return jsonify(
            error=err.__class__.__name__, message=str(err.orig)
        ), 400
    elif isinstance(err, HTTPException):
        return jsonify(
            error=err.__class__.__name__, message=str(err)
        ), err.code

    raise err
