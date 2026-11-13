from flask import render_template, redirect, request
from flask_login import login_required, current_user

def register_routes(app):
    """Register template routes"""
    roles = {
        'GUARDIAN': 'Guardian',
        'DRIVER': 'Driver',
        'STAFF': 'Staff',
    }
    
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.role == 'GUARDIAN':
                return redirect('/guardian/dashboard')
            elif current_user.role == 'DRIVER':
                return redirect('/driver/dashboard')
            elif current_user.role in ['ADMIN', 'SAFETY_ADMIN']:
                return redirect('/admin/dashboard')
            elif current_user.role == 'INSTITUTION_STAFF':
                return redirect('/admin/dashboard')
        return render_template('role_selection.html')
    
    @app.route('/login')
    def login_page():
        role = request.args.get('role', '').upper()
        if role not in roles:
            return redirect('/')
        return render_template('login.html', role=role, role_name=roles[role])
    
    @app.route('/register')
    def register_page():
        role = request.args.get('role', '').upper()
        if role not in ('GUARDIAN', 'DRIVER'):
            return redirect('/')
        return render_template('register.html', role=role, role_name=roles[role])
    
    @app.route('/guardian/dashboard')
    @login_required
    def guardian_dashboard():
        if current_user.role != 'GUARDIAN':
            return redirect('/')
        return render_template('guardian_dashboard.html')
    
    @app.route('/driver/dashboard')
    @login_required
    def driver_dashboard():
        if current_user.role != 'DRIVER':
            return redirect('/')
        return render_template('driver_dashboard.html')
    
    @app.route('/admin/dashboard')
    @login_required
    def admin_dashboard():
        if current_user.role not in ['ADMIN', 'SAFETY_ADMIN']:
            return redirect('/')
        return render_template('admin_dashboard.html')
    
    @app.route('/safety/dashboard')
    @login_required
    def safety_dashboard():
        if current_user.role != 'SAFETY_ADMIN':
            return redirect('/')
        return render_template('safety_dashboard.html')
