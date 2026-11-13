from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime

from backend.app.extensions import db
from backend.app.models import Student

bp = Blueprint('students', __name__, url_prefix='/api/v1/students')

@bp.route('', methods=['GET', 'POST'])
@login_required
def students():
    if request.method == 'POST':
        if current_user.role != 'GUARDIAN':
            return jsonify({'ok': False, 'error': {'message': 'Only guardians can add students'}}), 403
        
        data = request.get_json()
        
        student = Student(
            guardian_id=current_user.id,
            institution_id=data.get('institution_id'),
            first_name=data.get('first_name'),
            class_label=data.get('class_label'),
            dob=datetime.strptime(data.get('dob'), '%Y-%m-%d').date() if data.get('dob') else None,
            age_category=data.get('age_category', 'MINOR_SECONDARY'),
            status='ACTIVE'
        )
        db.session.add(student)
        db.session.commit()
        
        return jsonify({
            'ok': True,
            'data': {
                'student': {
                    'id': student.id,
                    'first_name': student.first_name,
                    'class_label': student.class_label
                }
            }
        }), 201
    
    else:
        # GET
        if current_user.role == 'GUARDIAN':
            students_list = Student.query.filter_by(guardian_id=current_user.id).all()
        else:
            students_list = Student.query.limit(100).all()
        
        return jsonify({
            'ok': True,
            'data': {
                'students': [{
                    'id': s.id,
                    'first_name': s.first_name,
                    'class_label': s.class_label,
                    'age_category': s.age_category,
                    'status': s.status
                } for s in students_list]
            }
        }), 200

@bp.route('/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
@login_required
def student(id):
    student = Student.query.get_or_404(id)
    
    # Authorization
    if current_user.role == 'GUARDIAN' and student.guardian_id != current_user.id:
        return jsonify({'ok': False, 'error': {'message': 'Unauthorized'}}), 403
    
    if request.method == 'GET':
        return jsonify({
            'ok': True,
            'data': {
                'student': {
                    'id': student.id,
                    'first_name': student.first_name,
                    'class_label': student.class_label,
                    'dob': student.dob.isoformat() if student.dob else None,
                    'age_category': student.age_category,
                    'status': student.status,
                    'institution_id': student.institution_id
                }
            }
        }), 200
    
    elif request.method == 'PATCH':
        if current_user.role != 'GUARDIAN':
            return jsonify({'ok': False, 'error': {'message': 'Unauthorized'}}), 403
        
        data = request.get_json()
        student.first_name = data.get('first_name', student.first_name)
        student.class_label = data.get('class_label', student.class_label)
        db.session.commit()
        
        return jsonify({'ok': True, 'data': {'message': 'Student updated'}}), 200
    
    elif request.method == 'DELETE':
        if current_user.role != 'GUARDIAN':
            return jsonify({'ok': False, 'error': {'message': 'Unauthorized'}}), 403
        
        student.status = 'INACTIVE'
        db.session.commit()
        
        return jsonify({'ok': True, 'data': {'message': 'Student deactivated'}}), 200
