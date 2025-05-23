from flask import Blueprint, flash, render_template, request, redirect, url_for
from .models import User, db
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            if (user.password == password or check_password_hash(user.password, password)):
                print("Logged in Successfully!")
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash("Incorrect password, please try again.", category="error")
        else:
            flash("Username does not exist!", category="error")

    return render_template("login.html", user=current_user)
@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    user_id = session.get('reset_user_id')
    if not user_id:
        flash("Session expired or unauthorized access.", category="error")
        return redirect(url_for('auth.login'))

    user = User.query.get(user_id)
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if new_password != confirm_password:
            flash("Passwords do not match.", category="error")
        else:
            user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
            db.session.commit()
            session.pop('reset_user_id', None)
            flash("Password reset successfully! Please login.", category="success")
            return redirect(url_for('auth.login'))

    return render_template('reset_password.html')

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        dob = request.form.get('dob')
        
        user = User.query.filter_by(username=email).first()
        if not user:
            flash("No user found with that email.", category="error")
        elif user.DOB != dob:
            flash("Date of birth does not match our records.", category="error")
        else:
            # Store user id in session for resetting
            session['reset_user_id'] = user.id
            return redirect(url_for('auth.reset_password'))
    
    return render_template('forgot_password.html')


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        dob = request.form.get('dob')
        user_type = request.form.get('user_type')
        student_level = request.form.get('student_level') if user_type == 'student' else None  # Added

        existing_user = User.query.filter_by(username=email).first()
        if existing_user:
            flash("Email already exists. Please use a different email.", category="error")
            return redirect(url_for('auth.signup'))

        new_user = User(
            username=email,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            first_name=firstName,
            last_name=lastName,
            DOB=dob,
            user_type=user_type,
            student_level=student_level  # Added
        )

        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully!", category="success")
        login_user(new_user, remember=True)
        return redirect(url_for('views.home'))

    return render_template("signup.html", user=current_user)

@auth.route('/settings', methods=['GET', 'POST'])
@login_required
def edit_details():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(username=email).first()
        if user:
            user.password = request.form.get('password')
            user.first_name = request.form.get('firstName')
            user.last_name = request.form.get('lastName')
            user.DOB = request.form.get('dob')
            db.session.commit()
            flash("Details updated successfully!", category="success")
            return redirect(url_for('views.home'))
        else:
            flash("User not found!", category="error")

    return render_template("settings.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
