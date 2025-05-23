import math
from flask_login import login_required, current_user
from flask import Blueprint, flash, jsonify, render_template, request, redirect, url_for
import magic
from werkzeug.utils import secure_filename
from .models import Discussion, Reply, User, db, Course, Request, Enrollment, Quiz, Essay, QuizQuestion, EssayQuestion, QuizSubmission, EssaySubmission
import base64
from werkzeug.security import generate_password_hash, check_password_hash
import os
from .models import LiveLesson
from .models import Notification


views = Blueprint('views', __name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'pptx', 'mp4', 'mp3', 'jpg', 'png', 'zip'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@views.route('/make-payment')
@login_required
def make_payment():
    return render_template('make_payment.html', user=current_user)
# views.py

@views.route('/course/<int:course_id>/live', methods=['GET', 'POST'])
@login_required
def manage_live(course_id):
    course = Course.query.get_or_404(course_id)
    if current_user.id != course.teacher_id:
        flash("Unauthorized", "error")
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        title = request.form.get('title')
        stream_url = request.form.get('stream_url')
        new_lesson = LiveLesson(course_id=course_id, title=title, stream_url=stream_url, is_active=True)
        db.session.add(new_lesson)
        db.session.commit()
        flash("Live lesson started!", "success")
        return redirect(url_for('views.view_live', lesson_id=new_lesson.id))

    return render_template("start_live.html", course=course)

@views.route('/live/<int:lesson_id>')
@login_required
def view_live(lesson_id):
    lesson = LiveLesson.query.get_or_404(lesson_id)
    return render_template("live_lesson.html", lesson=lesson)

@views.route('/process-payment', methods=['POST'])
@login_required
def process_payment():
    # Logic for processing payment goes here
    # Once payment is successful:
    current_user.has_paid = True
    db.session.commit()
    flash("Payment successful! You can now enroll in courses.", category="success")
    return redirect(url_for('views.display_courses'))


@views.route('/edit-course/<int:course_id>', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    if current_user.user_type != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('views.home'))
    course = Course.query.get_or_404(course_id)
    if request.method == 'POST':
        course.course_name = request.form['course_name']
        course.course_code = request.form['course_code']
        course.course_desc = request.form['course_desc']
        db.session.commit()
        flash('Course updated!', 'success')
        return redirect(url_for('views.home'))
    return render_template('edit_course.html', course=course)

@views.route('/delete-course/<int:course_id>')
@login_required
def delete_course(course_id):
    if current_user.user_type != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('views.home'))
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted!', 'success')
    return redirect(url_for('views.home'))

# Home Page (Dashboard)
@views.route('/')
@login_required
def home():
    enrolled_courses = Course.query.join(Enrollment).filter(Enrollment.user_id == current_user.id).all()
    all_courses = Course.query.all()
    notifications = Notification.query.filter_by(is_visible=True).order_by(Notification.created_at.desc()).limit(5).all()
    return render_template("dashboard.html", user=current_user, enrolled_courses=enrolled_courses, all_courses=all_courses, notifications=notifications)

# Account Details
@views.route('/accountDetails')
@login_required
def account_details():
    return render_template("accountDetails.html", user=current_user)

# Edit User Details Page
@views.route('/settings', methods=['GET', 'POST'])
@login_required
def edit_details():
    if request.method == 'POST':
        user = User.query.filter_by(username=current_user.username).first()      
        if user:
            new_password = request.form.get('password')
            if new_password is not None and new_password != "":
                user.password = generate_password_hash(new_password)

            new_first_name = request.form.get('firstName')
            if new_first_name is not None and new_first_name != "":
                user.first_name = new_first_name
            else:
                user.first_name = current_user.first_name

            new_last_name = request.form.get('lastName')
            if new_last_name is not None and new_last_name != "":
                user.last_name = new_last_name
            else:
                user.last_name = current_user.last_name

            new_dob = request.form.get('dob')
            if new_dob is not None and new_dob != "":
                user.DOB = new_dob
            else:
                user.DOB = current_user.DOB    
            db.session.commit()
            return redirect(url_for('views.account_details'))
        else:
            return redirect(url_for('views.edit_details'))
    return render_template("settings.html", user=current_user)

@views.route('/create-course', methods=['GET', 'POST'])
def createCourse():
    if request.method == 'POST':
        course_name = request.form.get('course_name')
        course_desc = request.form.get('course_desc')
        course_limit = request.form.get('course_limit')
        course_code = request.form.get('course_code')
        teacher_id = request.form.get('teacher_id')
        resource_link = request.form.get('resource_link')
        file = request.files.get('resources')

        filename = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))

        existing_course = Course.query.filter_by(course_code=course_code).first()
        if existing_course:
            flash('A course with this code already exists.', category='error')
            return redirect(url_for('views.createCourse'))
        else:
            new_course = Course(
                course_code=course_code,
                course_name=course_name,
                course_desc=course_desc,
                course_limit=course_limit,
                teacher_id=teacher_id,
                resources=filename,
                resource_link=resource_link,
                target_level = request.form.get('target_level')

            )
            db.session.add(new_course)
            db.session.commit()

            teacher_enrollment = Enrollment(user_id=teacher_id, course_id=new_course.id)
            db.session.add(teacher_enrollment)
            db.session.commit()
            return redirect(url_for('views.home'))

    teachers = User.query.filter_by(user_type='teacher').all()
    return render_template("createCourse.html", user=current_user, teachers=teachers)

@views.route('/create-request', methods=['POST'])
def createRequest():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        course_id = request.form.get('course_id')
        new_request = Request(user_id=user_id, course_id=course_id, status='pending')
        db.session.add(new_request)
        db.session.commit()
    return redirect(url_for('views.display_courses'))

@views.route('/enroll-courses')
@login_required
def display_courses():
    # Redirect unpaid students
    if current_user.user_type == 'student' and not current_user.has_paid:
        flash("You must complete payment before enrolling in courses.", category="error")
        return redirect(url_for('views.make_payment'))

    # Fetch IDs of courses the student already requested or enrolled in
    requested_course_ids = db.session.query(Request.course_id).filter_by(user_id=current_user.id).all()
    requested_course_ids = [r.course_id for r in requested_course_ids]

    enrolled_course_ids = db.session.query(Enrollment.course_id).filter_by(user_id=current_user.id).all()
    enrolled_course_ids = [e.course_id for e in enrolled_course_ids]

    # Fetch courses available for enrollment
    courses = db.session.query(
        Course.id, Course.course_code, Course.course_name, Course.course_desc,
        Course.course_limit, User.first_name, User.last_name
    ).join(User, Course.teacher_id == User.id)\
     .filter(Course.id.notin_(requested_course_ids + enrolled_course_ids)).all()

    # Fetch rejected enrollment requests
    rejected = db.session.query(
        Course.id, Course.course_code, Course.course_name, Course.course_desc,
        Course.course_limit, User.first_name, User.last_name
    ).join(Request, Request.course_id == Course.id)\
     .join(User, Course.teacher_id == User.id)\
     .filter(Request.user_id == current_user.id, Request.status == "declined").all()

    return render_template('enrollCourse.html', user=current_user, courses=courses, rejected=rejected)


@views.route('/requests')
def display_requests():
    requests = db.session.query(Request.id, Request.user_id,Request.course_id, Course.course_code,Request.status).join(Course, Request.course_id == Course.id).filter(Request.status == 'pending').all()
    return render_template('acceptCourse.html', requests=requests)

@views.route('/accept-request', methods=['POST'])
def acceptRequest():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        course_id = request.form.get('course_id')
        new_enrolment = Enrollment(user_id=user_id, course_id=course_id)
        db.session.add(new_enrolment)
        
        request_approved = Request.query.filter_by(user_id=user_id, course_id=course_id, status='pending').first()
        if request_approved:
            request_approved.status = "approved"
            db.session.commit()
        else:
            print("No pending request found for user_id:", user_id, "and course_id:", course_id)
        
    return redirect(url_for('views.display_requests'))

@views.route('/decline-request', methods=['POST'])
def declineRequest():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        course_id = request.form.get('course_id')
        all_requests = Request.query.filter_by(user_id=user_id, status='pending').all()
        print(f"All pending requests for user_id={user_id}: {[{'course_id': r.course_id, 'status': r.status} for r in all_requests]}")
        request_declined = Request.query.filter_by(user_id=user_id, course_id=course_id, status='pending').first()
        if request_declined:
            request_declined.status = "declined"
            db.session.commit()
        else:
            print(f"No pending request found for user_id={user_id}, course_id={course_id}")
    return redirect(url_for('views.display_requests'))
@views.route('/notifications')
@login_required
def list_notifications():
    notifications = Notification.query.order_by(Notification.created_at.desc()).all()
    return render_template('notifications/list.html', notifications=notifications)

@views.route('/notifications/create', methods=['GET', 'POST'])
@login_required
def create_notification():
    if request.method == 'POST':
        title = request.form.get('title')
        message = request.form.get('message')
        notification = Notification(title=title, message=message, created_by=current_user.id)
        db.session.add(notification)
        db.session.commit()
        flash('Notification created!')
        return redirect(url_for('list_notifications'))
    return render_template('notifications/create.html')

@views.route('/notifications/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_notification(id):
    notification = Notification.query.get_or_404(id)
    if request.method == 'POST':
        notification.title = request.form.get('title')
        notification.message = request.form.get('message')
        db.session.commit()
        flash('Notification updated!')
        return redirect(url_for('list_notifications'))
    return render_template('notifications/edit.html', notification=notification)

@views.route('/notifications/<int:id>/delete')
@login_required
def delete_notification(id):
    notification = Notification.query.get_or_404(id)
    db.session.delete(notification)
    db.session.commit()
    flash('Notification deleted!')
    return redirect(url_for('list_notifications'))
@views.route('/course/<int:course_id>')
@login_required
def course_page(course_id):
    course = Course.query.get(course_id)
    quizzes = Quiz.query.filter_by(course_id=course_id).all()
    essays = Essay.query.filter_by(course_id=course_id).all()
    teacher = User.query.get(course.teacher_id)
    # Get the active live stream for the course
    live_lesson = LiveLesson.query.filter_by(course_id=course.id, is_active=True).first()
    quiz_submissions = {}
    for quiz in quizzes:
        submissions = QuizSubmission.query.filter_by(quiz_id=quiz.id).all()
        quiz_submissions[quiz.id] = {}
        for submission in submissions:
            student = User.query.get(submission.student_id)
            student_name = student.first_name + " " + student.last_name
            quiz_submissions[quiz.id][submission.student_id] = {
                'student_name': student_name,
                'graded': submission.given_grade is not None
            }

    essay_submissions = {}
    for essay in essays:
        submissions = EssaySubmission.query.filter_by(essay_id=essay.id).all()
        essay_submissions[essay.id] = {}
        for submission in submissions:
            student = User.query.get(submission.student_id)
            student_name = student.first_name + " " + student.last_name
            essay_submissions[essay.id][submission.student_id] = {
                'student_name': student_name,
                'graded': submission.given_grade is not None
            }

    return render_template(
        'course.html',
        course=course,
        teacher=teacher,
        quizzes=quizzes,
        essays=essays,
        quiz_submissions=quiz_submissions,
        essay_submissions=essay_submissions,
        live_lesson=live_lesson  # Add this to make it available in the template
    )

@views.route('/course/<int:course_id>/createAssignment', methods=['GET','POST'])
def createAssignment(course_id):
    if request.method == 'POST':
        assignment_type = request.form.get('assignmentType')
        assignment_name = request.form.get('title')

        if assignment_type == 'quiz':
            new_quiz = Quiz(quiz_name=assignment_name, course_id=course_id)
            db.session.add(new_quiz)
            db.session.commit()

            question_keys = [key for key in request.form if key.startswith('question')]
            for question_key in question_keys:
                question_number = question_key[len('question'):]
                question_text = request.form[question_key]
                question_max_grade = request.form.get(f'question-max-grade{question_number}')
                options = [request.form.get(f'option{question_number}-{i}') for i in range(1, 4)]
                quiz_question = QuizQuestion(question_text=question_text, quiz_id=new_quiz.id, option1=options[0], option2=options[1], option3=options[2], max_grade=question_max_grade)
                db.session.add(quiz_question)

        else:
            new_essay = Essay(essay_name=assignment_name, course_id=course_id)
            db.session.add(new_essay)
            db.session.commit()
            essay_text = None
            essay_file = None

            question_type = request.form.get('contentMethodEssay')
            if question_type == 'text':
                essay_text = request.form.get('text-entry-essay')
            elif 'file-upload-essay' in request.files:
                file = request.files['file-upload-essay']
                if file and file.filename != '':
                    essay_file = file.read()
            essay_max_grade = request.form.get('essay-max-grade')
            essay_question = EssayQuestion(essay_id = new_essay.id, question_type = question_type, file_upload = essay_file, question_text = essay_text, max_grade = essay_max_grade)
            db.session.add(essay_question)

        db.session.commit()
        return redirect(url_for('views.course_page', course_id=course_id))

    return render_template('createAssignment.html', user=current_user, course_id=course_id)

@views.route('/course/<int:course_id>/quiz/<int:quiz_id>',methods=['GET'])
def quiz_page(course_id, quiz_id):
    quiz = Quiz.query.filter_by(id=quiz_id, course_id=course_id).first()
    questions = QuizQuestion.query.filter_by(quiz_id=quiz_id).all()
    already_submitted = QuizSubmission.query.filter_by(quiz_id=quiz_id, student_id=current_user.id).first()
    return render_template('quiz.html', course_id=course_id, questions=questions, quiz=quiz, already_submitted=already_submitted)

@views.route('/submit_quiz',methods=['POST'])
def submit_quiz():
    quiz_id = request.form.get('quiz_id')
    student_id = current_user.id
    course_id = request.form.get('course_id')
    question_ids = [question.id for question in QuizQuestion.query.filter_by(quiz_id=quiz_id).all()]
    
    for key in request.form:
        if key not in ['quiz_id', 'course_id'] and key.isdigit() and int(key) in question_ids:
            selected_option = request.form[key]
            existing_submission = QuizSubmission.query.filter_by(
                quiz_id=quiz_id,
                student_id=student_id,
                quizQuestion_id=key
            ).first()
            if not existing_submission:
                submission = QuizSubmission(
                    selected_option=selected_option,
                    quiz_id=quiz_id,
                    quizQuestion_id=key,
                    student_id=student_id
                )
                db.session.add(submission)

    db.session.commit()
    return redirect(url_for('views.course_page', course_id=course_id))

@views.route('/course/<int:course_id>/essay/<int:essay_id>', methods=['GET'])
def essay_page(course_id, essay_id):
    essay = Essay.query.filter_by(id=essay_id, course_id=course_id).first()
    questions = EssayQuestion.query.filter_by(essay_id=essay_id).all()
    for question in questions:
        if question.file_upload and question.question_type == 'file':
            question.base64_image = base64.b64encode(question.file_upload).decode('utf-8')
    student_id = current_user.id 
    already_submitted = EssaySubmission.query.filter_by(essay_id=essay_id, student_id=current_user.id).first()  
    return render_template('essay.html', course_id=course_id, questions=questions, essay=essay,student_id=student_id, already_submitted=already_submitted)

@views.route('/submit_essay', methods=['POST'])
def submit_essay():
    essay_id = request.form.get('essay_id')
    student_id = request.form.get('student_id')
    course_id = request.form.get('course_id')

    for key, value in request.form.items():
        if key.startswith('text_answer'):
            question_id = key.replace('text_answer', '')
            if value:
                new_submission = EssaySubmission(answer_text=value, answer_file=None, answer_type='text', essay_id=essay_id, essayQuestion_id=question_id, student_id=student_id)
                db.session.add(new_submission)

    for file_key in request.files:
        if file_key.startswith('file_answer'):
            question_id = file_key.replace('file_answer', '')
            file = request.files[file_key]
            if file and file.filename != '':
                essay_file = file.read()         
                new_submission = EssaySubmission(answer_text=None, answer_file=essay_file, answer_type='file', essay_id=essay_id, essayQuestion_id=question_id, student_id=student_id)
                db.session.add(new_submission) 

    db.session.commit()
    return redirect(url_for('views.course_page', course_id=course_id))

@views.route('/course/<int:course_id>/view-grade',methods=['GET'])
def grade_page(course_id):        
    quizzes = Quiz.query.filter_by(course_id=course_id).all()
    essays = Essay.query.filter_by(course_id=course_id).all()
    student_id = current_user.id
    quiz_grades = {}
    for quiz in quizzes:
        quiz_questions = QuizQuestion.query.filter_by(quiz_id=quiz.id).all()
        quiz_max_grade = sum(question.max_grade if question.max_grade is not None else 1 for question in quiz_questions)

        quiz_submissions = QuizSubmission.query.filter_by(quiz_id=quiz.id, student_id=student_id).all()
        if quiz_submissions and any(submission.given_grade is not None for submission in quiz_submissions):
            total_grade = sum(submission.given_grade for submission in quiz_submissions if submission.given_grade is not None)
            total_grade =str(round((total_grade / quiz_max_grade * 100), 2))+"%"
        else:
            total_grade = "N/A"
        quiz_grades[quiz.id] = total_grade
        
    essay_grades = {}
    for essay in essays:
        essay_question = EssayQuestion.query.filter_by(essay_id=essay.id).first()
        essay_max_grade = essay_question.max_grade if essay_question.max_grade is not None else 100
        essay_submissions = EssaySubmission.query.filter_by(essay_id=essay.id, student_id=student_id).all()
        if essay_submissions and any(submission.given_grade is not None for submission in essay_submissions):
            total_grade = sum(submission.given_grade for submission in essay_submissions if submission.given_grade is not None)
            total_grade =str(round((total_grade / essay_max_grade * 100), 2))+"%"
        else:
            total_grade = "N/A"
        essay_grades[essay.id] = total_grade
    
    return render_template('viewGrade.html', course_id=course_id, quizzes=quizzes, essays=essays, quiz_grades=quiz_grades, essay_grades=essay_grades)

@views.route('/course/<int:course_id>/discussions',  methods=['GET'])
@login_required
def course_discussions(course_id):
    course = Course.query.get_or_404(course_id)
    discussions = Discussion.query.filter_by(course_id=course_id).all()
    course_full_name = f"{course.course_code} {course.course_name}" 
    return render_template('discussion.html', course_name=course_full_name, course=course, discussions=discussions, course_id=course_id)

@views.route('/course/<int:course_id>/discussion/<int:discussion_id>')
@login_required
def discussion_detail(discussion_id, course_id):
    discussion = Discussion.query.get_or_404(discussion_id)
    discussion_author = User.query.get(discussion.user_id).username
    replies = db.session.query(Reply, User.username).join(User, User.id == Reply.user_id).filter(Reply.discussion_id == discussion_id).all()
    return render_template('discussion_detail.html', discussion=discussion, discussion_author=discussion_author, replies=replies, course_id=course_id)

@views.route('/course/<int:course_id>/discussions/add', methods=['GET', 'POST'])
@login_required
def add_discussion(course_id):
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        new_discussion = Discussion(title=title, content=content, course_id=course_id, user_id=current_user.id)
        db.session.add(new_discussion)
        db.session.commit()
        return redirect(url_for('views.course_discussions', course_id=course_id))
    return render_template('add_discussion.html', course_id=course_id)

@views.route('/course/<int:course_id>/discussion/<int:discussion_id>/submit_reply', methods=['POST'])
@login_required
def submit_reply(discussion_id, course_id):
    content = request.form.get('reply_content')
    new_reply = Reply(content=content, discussion_id=discussion_id, user_id=current_user.id)
    db.session.add(new_reply)
    db.session.commit()
    return redirect(url_for('views.discussion_detail', discussion_id=discussion_id, course_id=course_id))

@views.route('/grade-quiz/<int:course_id>/<int:quiz_id>/<int:student_id>', methods=['GET', 'POST'])
@login_required
def grade_quiz(course_id, quiz_id, student_id):
    quiz = Quiz.query.get(quiz_id)
    student = User.query.get(student_id)
    quiz_questions = QuizQuestion.query.filter_by(quiz_id=quiz_id).all()
    quiz_submissions = QuizSubmission.query.filter_by(quiz_id=quiz_id, student_id=student_id).all()

    for submission in quiz_submissions:
        question_for_submission = next((question for question in quiz_questions if question.id == submission.quizQuestion_id), None)
        if question_for_submission is not None:
            submission.question_text = question_for_submission.question_text
            submission.question_option1 = question_for_submission.option1
            submission.question_option2 = question_for_submission.option2
            submission.question_option3 = question_for_submission.option3
            submission.max_grade = question_for_submission.max_grade if question_for_submission.max_grade else 1

    quiz.quiz_max_grade = sum(question.max_grade if question.max_grade is not None else 1 for question in quiz_questions)

    if request.method == 'POST':
        all_grades_valid = True
        for submission in quiz_submissions:
            grade_str = request.form.get(f'grade_{submission.id}')
            try:
                grade = int(grade_str) if grade_str is not None else None
            except ValueError:
                grade = None
            if grade is None or not (0 <= grade <= submission.max_grade):
                all_grades_valid = False
                break
            else:
                submission.given_grade = grade
        if all_grades_valid:
            db.session.commit()
            return redirect(url_for('views.course_page', course_id=course_id))
        else:
            return render_template('gradeQuiz.html', course_id=course_id, quiz=quiz, student=student, submissions=quiz_submissions)
    
    return render_template('gradeQuiz.html', course_id=course_id, quiz=quiz, student=student, submissions=quiz_submissions)

@views.route('/grade-essay/<int:course_id>/<int:essay_id>/<int:student_id>', methods=['GET', 'POST'])
@login_required
def grade_essay(course_id, essay_id, student_id):
    essay = Essay.query.get(essay_id)
    student = User.query.get(student_id)
    essay_question = EssayQuestion.query.filter_by(essay_id=essay_id).first()
    essay_submission = EssaySubmission.query.filter_by(essay_id=essay_id, student_id=student_id).first()

    question_data_uri = None
    answer_data_uri = None

    essay_submission.max_grade = essay_question.max_grade if essay_question.max_grade is not None else 100

    if essay_question.question_type == 'text':
        essay_submission.question_text = essay_question.question_text
    elif essay_question.file_upload and essay_question.question_type == 'file':
        mime_type = magic.from_buffer(essay_question.file_upload, mime=True)
        base64_file = base64.b64encode(essay_question.file_upload).decode('utf-8')
        question_data_uri = f'data:{mime_type};base64,{base64_file}'

    if essay_submission.answer_type == 'file' and essay_submission.answer_file:
        mime_type = magic.from_buffer(essay_submission.answer_file, mime=True)
        base64_file = base64.b64encode(essay_submission.answer_file).decode('utf-8')
        answer_data_uri = f'data:{mime_type};base64,{base64_file}'
    else:
        essay_submission.answer_text = essay_submission.answer_text if essay_submission.answer_text else ''

    if request.method == 'POST':
        grade_str = request.form.get('essay-grade')
        try:
            essay_grade = int(grade_str) if grade_str else None
        except ValueError:
            essay_grade = None

        if essay_grade is not None and 0 <= essay_grade <= essay_submission.max_grade:
            essay_submission.given_grade = essay_grade
            db.session.commit()
            return redirect(url_for('views.course_page', course_id=course_id))

    return render_template('gradeEssay.html', course_id=course_id, essay=essay, question=essay_question, student=student, question_data_uri=question_data_uri, submission=essay_submission, answer_data_uri=answer_data_uri)

@views.route('/instantiate-db')
def instantiate_db():
    new_user1 = User(username="stu@gmail.com",password=1,first_name="Jonathan",last_name="Trott",DOB="2024-03-29",user_type="student")
    db.session.add(new_user1)
    new_user2 = User(username="teach@gmail.com",password=2,first_name="David",last_name="Latham",DOB="2024-03-20",user_type="teacher")
    db.session.add(new_user2)
    new_user3 = User(username="admin@gmail.com",password=3,first_name="Kim",last_name="Yong",DOB="2024-03-25",user_type="admin")
    db.session.add(new_user3)
    db.session.commit()
    
    new_course1 = Course(course_code="Math 100", course_name="Differential Calculus", course_desc="Introduction to derivatives and rate of change", course_limit=120, teacher_id=2)
    db.session.add(new_course1)
    new_course2 = Course(course_code="DATA 101", course_name="Intro to R Programming", course_desc="Introduction to basic programming and related concepts", course_limit=90, teacher_id=2)
    db.session.add(new_course2)
    db.session.commit()
    
    teacher_enrollment1 = Enrollment(user_id=2,course_id=1)
    db.session.add(teacher_enrollment1)
    student_enrollment1 = Enrollment(user_id=1,course_id=1)
    db.session.add(student_enrollment1)
    student_enrollment2 = Enrollment(user_id=1,course_id=2)
    db.session.add(student_enrollment2)
    db.session.commit() 
    
    return "<h3>Instantiated DB</h3>"
