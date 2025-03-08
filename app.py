from flask import Flask, render_template, request, jsonify, session, redirect, flash, url_for, send_from_directory
from flask_cors import CORS
from pymysql import connections
import os
import boto3
from config import *
import datetime
import secrets
import subprocess
import re
import logging
from werkzeug.utils import secure_filename
from urllib.parse import unquote
from algorithm.Identification.ImageComparison import identify_faces
from algorithm.Verification.PDFKeyword import extract_specific_words
from algorithm.Verification.PDFReader import extract_bottom_text_from_pdf

app = Flask(__name__)
CORS(app)
app.secret_key = secrets.token_hex(16)
bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb
)
output = {}
table = 'ExamAttendance'

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('Overall/index.html')

@app.route('/Overall/index.html',methods=['GET','POST'])
def index():
    return render_template('Overall/index.html')

@app.route('/Overall/studentLogin.html',methods=['GET','POST'])
def login2():
    return render_template('Overall/studentLogin.html')

@app.route('/Overall/lecturerLogin.html',methods=['GET','POST'])
def login3():
    return render_template('Overall/lecturerLogin.html')

@app.route('/Overall/profile.html', methods=['GET', 'POST'])
def profile():
    students = getStudent()
    return render_template('Overall/profile.html', students=students)

@app.route('/ExamManagement/examdetail.html', methods=['GET', 'POST'])
def examDetail():
    result_list = get_exam()
    return render_template('ExamManagement/examdetail.html', result_list=result_list)

@app.route('/ExamManagement/exammanage.html',methods=['GET','POST'])
def manage():
    available_venue_ids = selectionOption()
    return render_template('ExamManagement/exammanage.html', available_venue_ids=available_venue_ids)

@app.route('/StudentManagement/studentdetail.html',methods=['GET','POST'])
def studentDetail():
    result_list = get_student_info()
    return render_template('StudentManagement/studentdetail.html', result_list=result_list)

@app.route('/IdentificationAndVerification/identificationCamera.html', methods=['GET','POST'])
def cameraImage():
    student_verify_value = select_student_verify()
    return render_template('IdentificationAndVerification/identificationCamera.html', student_verify_value=student_verify_value)

@app.route("/studentlogin",methods=['POST'])
def studentlogin():
    student_id = request.form['student_id']
    student_password = request.form['student_password']

    student_login_query = "SELECT * FROM Student where student_id = %s AND student_password = %s"
    cursor = db_conn.cursor()
    cursor.execute(student_login_query, (student_id, student_password))
    student_data_list = cursor.fetchall()
    cursor.close()
    if student_data_list:
        student_data = student_data_list[0]
        student = dict(zip([column[0] for column in cursor.description], student_data))
        session["user"] = {"student_id": student["student_id"], "role": "student"}
        flash("Login successful!", "success")
        print("done!")
        #return "done!"
        return render_template("Overall/index.html")
    else:
        flash("Login failed. Invalid student ID or password","error")
        print("error")
        return render_template("Overall/index.html", login_error=True)

@app.route("/lecturerlogin",methods=['POST'])
def lecturelogin():
    lecturer_id = request.form['lecturer_id']
    lecturer_password = request.form['lecturer_password']

    query = "SELECT * FROM Lecturer where lecturer_id = %s AND lecturer_password = %s"
    cursor = db_conn.cursor()
    cursor.execute(query, (lecturer_id, lecturer_password))
    lecture_data_list = cursor.fetchall()
    cursor.close()
    if lecture_data_list:
        lecture_data = lecture_data_list[0]
        lecture = dict(zip([column[0] for column in cursor.description], lecture_data))
        session["user"] = {"lecturer_id": lecture["lecturer_id"], "role": "lecturer"}
        flash("Login successful!", "success")
        print("done!")
        #return "done!"
        return render_template("Overall/index.html")
    else:
        flash("Login failed. Invalid lecturer ID or password","error")
        print("error")
        return render_template("Overall/index.html", login_error=True)

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user', None)
    flash('You have been logged out', 'success')
    return render_template("Overall/index.html")

# def getPdfvalue():
#     try:
#         student_id = session.get('user', {}).get('student_id')
#         if not student_id:
#             return jsonify({'error': 'User not authenticated'}), 401
#         query = "SELECT student_uploadedfile FROM Student WHERE student_id = %s"
#         cursor = db_conn.cursor()
#         cursor.execute(query, student_id)
#         pdf_path = cursor.fetchone()[0]
#         print(pdf_path)
#         extracted_text = extract_bottom_text_from_pdf(pdf_path)
#         return jsonify({'success': True, 'extracted_text': extracted_text})
#     except Exception as e:
#         print(f"An unexpected error occurred: {str(e)}")
#         return jsonify({'success': False, 'error': f"An unexpected error occurred: {str(e)}"})
#     finally:
#         cursor.close()

# @app.route('/get_pdf_path', methods=['GET'])
# def get_pdf_path():
#     try:
#         student_id = session.get('user', {}).get('student_id')
#         if not student_id:
#             return jsonify({'error': 'User not authenticated'}), 401

#         query = "SELECT student_uploadedfile FROM Student WHERE student_id = %s"
#         cursor = db_conn.cursor()
#         cursor.execute(query, (student_id,))
#         pdf_path = cursor.fetchone()[0]
#         return jsonify({'success': True, 'pdf_path': pdf_path})
#     except Exception as e:
#         print(f"An unexpected error occurred: {str(e)}")
#         return jsonify({'success': False, 'error': f"An unexpected error occurred: {str(e)}"})
#     finally:
#         cursor.close()

@app.route("/getStudent", methods=['GET'])
def getStudent():
    try:
        student_id = session.get('user', {}).get('student_id')
        if not student_id:
            return "Missing studentID parameter", 400

        query = "SELECT student_profileimage, student_verify, student_id, student_name, student_gender, student_email, student_status, student_uploadedfile FROM Student WHERE student_id = %s"
        cursor = db_conn.cursor()
        cursor.execute(query, (student_id,))
        columns = [column[0] for column in cursor.description]
        student_data = dict(zip(columns, cursor.fetchone()))
        #student_data['student_uploadedfile'] = os.path.basename(student_data['student_uploadedfile'])
        base_path = os.path.abspath(os.path.dirname(__file__))
        student_data['student_profileimage'] = os.path.relpath(student_data['student_profileimage'], base_path)

        print(student_data)
        return student_data
    except Exception as e:
        print(str(e))
        return "An error has occurred"
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()

UPLOADIMAGE_FOLDER = 'C:\FYPCode\static\\assets\img'
app.config['UPLOADIMAGE_FOLDER'] = UPLOADIMAGE_FOLDER

ALLOWEDIMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowedimage_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWEDIMAGE_EXTENSIONS

@app.route('/upload_profile_image', methods=['POST', 'GET'])
def upload_profile_image():
    try:
        student_id = session.get('user', {}).get('student_id')
        if not student_id:
            flash("User not authenticated", "error")
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401

        if request.method == 'POST':
            if 'fileInput' not in request.files:
                flash('No file part', 'error')
                print('No file part', 'error')
                return redirect(request.url)

            file = request.files['fileInput']

            if file.filename == '':
                flash('No selected file', 'error')
                print('No selected file', 'error')
                return redirect(request.url)

            if file and allowedimage_file(file.filename):
            # Generate a secure filename to avoid potential security issues
                filename = secure_filename(file.filename)

                file_path = os.path.join(app.config['UPLOADIMAGE_FOLDER'], filename)
                file.save(file_path)
                print(file_path)
                update_profile_image_query = "UPDATE Student SET student_profileimage = %s WHERE student_id = %s"
                cursor = db_conn.cursor()
                cursor.execute(update_profile_image_query, (file_path, student_id))
                db_conn.commit()
                flash('Profile picture updated successfully', 'success')
                return jsonify({'success': True, 'message': 'Profile picture updated successfully'})

    except Exception as e:
        flash(f"An error has occurred: {str(e)}", "error")
        return jsonify({'success': False, 'error': str(e)})
    finally:
        cursor.close()

UPLOADSLIP_FOLDER = 'C:/FYPCode/Uploads'
app.config['UPLOADSLIP_FOLDER'] = UPLOADSLIP_FOLDER

ALLOWEDSLIP_EXTENSIONS = {'pdf'}

def allowedslip_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWEDSLIP_EXTENSIONS

@app.route('/upload_slip', methods=['POST', 'GET'])
def uploadSlip():
    try:
        student_id = session.get('user', {}).get('student_id')
        if not student_id:
            flash("User not authenticated", "error")
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        if request.method == 'POST':
            if 'fileInput' not in request.files:
                flash('No file part', 'error')
                print('No file part', 'error')
                return redirect(request.url)

            file = request.files['fileInput']

            if file.filename == '':
                flash('No selected file', 'error')
                print('No selected file', 'error')
                return redirect(request.url)

            if file and allowedslip_file(file.filename):
            # Generate a secure filename to avoid potential security issues
                filename = secure_filename(file.filename)

                file_path = os.path.join(app.config['UPLOADSLIP_FOLDER'], filename)
                file.save(file_path)
                print(file_path)
                update_profile_image_query = "UPDATE Student SET student_uploadedfile = %s WHERE student_id = %s"
                cursor = db_conn.cursor()
                cursor.execute(update_profile_image_query, (file_path, student_id))
                db_conn.commit()
                # getPdfvalue()
                flash('Exam slip uploaded successfully', 'success')
                return jsonify({'success': True, 'message': 'Exam slip uploaded successfully'})
    except Exception as e:
        flash(f"An error has occurred: {str(e)}", "error")
        return jsonify({'success': False, 'error': str(e)})
    finally:
        cursor.close()

@app.route('/getExam', methods=['GET'])
def get_exam():
    try:
        exam_query = """
            SELECT Exam.exam_id, Exam.exam_date, Exam.exam_starttime, Exam.exam_endtime,
                   Exam.venue_id, Exam.course_code,
                   Course.course_name, Venue.venue_capacity,
                   GROUP_CONCAT(StudentExam.student_id) AS student_ids
            FROM Exam
            JOIN Course ON Exam.course_code = Course.course_code
            JOIN Venue ON Exam.venue_id = Venue.venue_id
            LEFT JOIN StudentExam ON Exam.exam_id = StudentExam.exam_id
            GROUP BY Exam.exam_id
        """
        cursor = db_conn.cursor()
        cursor.execute(exam_query)
        combined_result = cursor.fetchall()

        result_list = []
        for row in combined_result:
            result_list.append({
                'exam_id': row[0],
                'venue_id': row[4], 
                'course_code': row[5],
                'course_name': row[6],
                'exam_date': row[1],
                'exam_starttime': row[2],
                'exam_endtime': row[3]
            })
            print(result_list)
        return result_list
    except Exception as e:
        print(str(e))
        return jsonify({'error': 'An error has occurred'})
    finally:
        cursor.close()

@app.route('/exammanage', methods=['POST'])
def exammanage():
    try:
        venue_id = request.form['venue_id']
        venue_capacity = request.form['venue_capacity']
        course_faculty = request.form['course_faculty']
        course_code = request.form['course_code']
        course_name = request.form['course_name']
        exam_id = request.form['exam_id']
        exam_date = request.form['exam_date']
        exam_starttime = request.form['exam_starttime']
        exam_endtime = request.form['exam_endtime']

        if not all([venue_id, venue_capacity, course_faculty, course_code, course_name, exam_id, exam_date, exam_starttime, exam_endtime]):
            return jsonify({'success': False, 'error': 'Missing required fields'})
        
        with db_conn.cursor() as cursor:
            cursor.execute("INSERT INTO Venue (venue_id, venue_capacity) VALUES (%s, %s)", (venue_id, venue_capacity))
            cursor.execute("INSERT INTO Course (course_code, course_name, course_faculty) VALUES (%s, %s, %s)", (course_code, course_name, course_faculty))
            cursor.execute("INSERT INTO Exam (exam_id, exam_date, exam_starttime, exam_endtime, venue_id, course_code) VALUES (%s, %s, %s, %s, %s, %s)",
                           (exam_id, exam_date, exam_starttime, exam_endtime, venue_id, course_code))
        db_conn.commit()
        return render_template("ExamManagement/examdetail.html")
    except Exception as e:
        print(str(e))
        db_conn.rollback() 
        return jsonify({'success': False, 'error': str(e)})

@app.route('/venueid', methods=['GET'])
def selectionOption():
    try:
        option_query = "SELECT venue_id FROM Exam"
        cursor = db_conn.cursor()
        cursor.execute(option_query)
        venue_ids_from_db = [row[0] for row in cursor.fetchall()]
        cursor.close()

        hardcoded_venue_ids = ["R1", "R2", "PA1", "PA2", "V1", "V2", "SB1", "SB2"]
        available_venue_ids = list(set(hardcoded_venue_ids) - set(venue_ids_from_db))

        if not available_venue_ids:
            raise ValueError("Invalid or empty available_venue_ids list")
        return available_venue_ids
    except Exception as e:
        print(str(e))
        db_conn.rollback()
        return jsonify({'success': False, 'error': str(e)})

# def is_timetable_clash(venue_id, exam_date, exam_starttime, exam_endtime):
#     # Check if there is a timetable clash for the given venue, date, and time range
#     with db_conn.cursor() as cursor:
#         clash_query = """
#             SELECT 1
#             FROM Exam
#             WHERE venue_id = %s
#                 AND exam_date = %s
#                 AND ((exam_starttime <= %s AND exam_endtime >= %s)
#                      OR (exam_starttime <= %s AND exam_endtime >= %s))
#         """
#         cursor.execute(clash_query, (venue_id, exam_date, exam_starttime, exam_starttime, exam_endtime, exam_endtime))
#         return cursor.fetchone() is not None

@app.route('/updateExam', methods=['POST'])
def updateExam():
    try:
        exam_id = request.form['exam_id']
        venue_id = request.form['venue_id']
        course_code = request.form['course_code']
        course_name = request.form['course_name']
        exam_date = request.form['exam_date']
        exam_starttime = request.form['exam_starttime']
        exam_endtime = request.form['exam_endtime']

        update_exam_query = """
            UPDATE Exam
            JOIN Course ON Exam.course_code = Course.course_code
            SET
                Exam.venue_id = %s,
                Exam.course_code = %s,
                Course.course_name = %s,
                Exam.exam_date = %s,
                Exam.exam_starttime = %s,
                Exam.exam_endtime = %s
            WHERE
                Exam.exam_id = %s;
        """
        cursor = db_conn.cursor()
        cursor.execute(update_exam_query, (venue_id, course_code, course_name, exam_date, exam_starttime, exam_endtime, exam_id))
        db_conn.commit()
        cursor.close()
        return render_template("Overall/index.html")
        return jsonify({'success': True})
    except Exception as e:
        print(str(e))
        return jsonify({'success': False, 'error': str(e)})

@app.route("/deleteExam",methods=['POST'])
def deleteExam():
    venue_id = request.form['venue_id']
    course_code = request.form['course_code']
    exam_id = request.form['exam_id']
    delete_exam_query = "DELETE FROM Exam WHERE exam_id = %s"
    delete_venue_query = "DELETE FROM Venue WHERE venue_id = %s"
    delete_course_query = "DELETE FROM Course WHERE course_code = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(delete_exam_query, (exam_id))
        cursor.execute(delete_venue_query, (venue_id))
        cursor.execute(delete_course_query, (course_code))
        db_conn.commit()
        return render_template('Overall/index.html')
    except Exception as e:
        print(str(e))
        return f"An error has occurred: {str(e)}"
    finally:
        cursor.close()

@app.route('/capture_images', methods=['POST'])
def identificationCamera():
    script_folder = os.path.join(os.path.dirname(__file__), 'algorithm')
    script_path = os.path.join(script_folder, 'C:\FYPCode/algorithm\Identification\ImageCapture.py')
    try:
        subprocess.run(['python', script_path])
        result = {'success': True, 'message': 'Exit Camera Frame Successfully!'}
    except Exception as e:
        result = {'success': False, 'message': str(e)}
    return jsonify(result)

def get_profile_image_path(student_id):
    try:
        with db_conn.cursor() as cursor:
            query = "SELECT student_profileimage FROM Student WHERE student_id = %s"
            cursor.execute(query, (student_id,))
            result = cursor.fetchone()

            if result:
                return result[0]  
    except Exception as e:
        print(f"Error in get_profile_image_path: {str(e)}")

    return None 

@app.route('/get_comparison_result', methods=['POST'])
def get_comparison_result():
    try:
        card_image_path = "C:\FYPCode\captured_image_1.jpg" 
        student_id = session.get('user', {}).get('student_id')
        if not student_id:
            return jsonify({'error': 'User not authenticated'}), 401

        profile_image_path = get_profile_image_path(student_id)

        similarity_percentage, message = identify_faces(card_image_path, profile_image_path)
        threshold = 55

        print("Similarity Percentage:", similarity_percentage)
        print(message)

        return jsonify({'similarity_percentage': similarity_percentage, 'message': message, 'threshold': threshold})
    except Exception as e:
        error_message = str(e)
        print("Error:", error_message)
        return jsonify({'error': error_message})
    
@app.route('/capture_PDF', methods=['POST'])
def VerificationCamera():
    script_folder = os.path.join(os.path.dirname(__file__), 'algorithm')
    script_path = os.path.join(script_folder, 'C:\FYPCode/algorithm\Verification\PDFCapture.py')
    try:
        subprocess.run(['python', script_path])
        result = {'success': True, 'message': 'Exit Camera Frame Successfully!'}
    except Exception as e:
        result = {'success': False, 'message': str(e)}
    
    return jsonify(result)

UPLOAD_FOLDER = 'C:/FYPCode/Uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

logging.basicConfig(level=logging.DEBUG)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file submitted'})

    file = request.files['file']

    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'})

    logging.debug('Received file: %s', file.filename)  

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
    file.save(file_path)
    logging.debug('File saved to: %s', file_path)  # Log the file path
    
    ai_program_path = 'C:\FYPCode/algorithm\Verification\PDFExtract.py'  
    os.environ['FILE_PATH'] = file_path
    subprocess.run(['python', ai_program_path, file_path])

    return jsonify({'file_path': file_path})

@app.route('/get_pdf_comparison_result', methods=['POST'])
def get_pdf_comparison_result():
    #getPdfvalue()
    script_folder = os.path.join(os.path.dirname(__file__), 'algorithm')
    script_path = os.path.join(script_folder, 'C:\FYPCode/algorithm\Verification\PDFComparison.py')
    try:
        result = subprocess.check_output(['python', script_path], text=True)
        if result is None:
            return jsonify({'error': 'Subprocess returned None'})
        similarity_percentage, message = result.strip().splitlines()
        similarity_percentage = float(re.search(r'\d+\.\d+', result).group())
        threshold = 81 

        print("Similarity Percentage:", similarity_percentage)
        print(message)

        return jsonify({'similarity_percentage': similarity_percentage, 'message': message, 'threshold': threshold})
    except Exception as e:
        error_message = str(e)
        print("Error:", error_message)
        return jsonify({'error': error_message})

@app.route("/select_student_verify", methods=['GET'])
def select_student_verify():
    try:
        student_id = session.get('user', {}).get('student_id')
        if not student_id:
            return jsonify({'error': 'User not authenticated'}), 401
        select_studentverify_query = "SELECT student_verify FROM Student WHERE student_id = %s"
        cursor = db_conn.cursor()
        cursor.execute(select_studentverify_query, (student_id,))
        student_verify = cursor.fetchone()
        db_conn.commit()
        if student_verify is not None:
            student_verify_value = student_verify[0]
            return student_verify_value
        else:
            return jsonify({'success': False, 'error': 'Student not found'})

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return jsonify({'success': False, 'error': f"An unexpected error occurred: {str(e)}"})

@app.route('/update_student_verify', methods=['POST'])
def update_student_verify():
    db_conn.ping()
    try:
        student_id = session.get('user', {}).get('student_id')
        if not student_id:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Update student_verify
        update_student_query = "UPDATE Student SET student_verify = 1 WHERE student_id = %s"
        cursor = db_conn.cursor()
        cursor.execute(update_student_query, student_id)
        db_conn.commit()

        # retrieve student_uploadedfile 
        fetch_pdf_path_query = "SELECT student_uploadedfile FROM Student WHERE student_id = %s"
        cursor.execute(fetch_pdf_path_query, student_id)
        pdf_path = cursor.fetchone()[0]

        # Update student_indexnumber
        index_number_pattern = re.compile(r'\bW\w{9}\b')
        extracted_index_numbers = extract_specific_words(pdf_path, index_number_pattern)

        if extracted_index_numbers:
            student_indexnumber = extracted_index_numbers
            update_index_query = "UPDATE Student SET student_indexnumber = %s WHERE student_id = %s"
            cursor.execute(update_index_query, (student_indexnumber, student_id))
            db_conn.commit()
        cursor.close()
        return jsonify({'success': True})
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return jsonify({'success': False, 'error': f"An unexpected error occurred: {str(e)}"})

@app.route('/getStudentInfo', methods=['GET'])
def get_student_info():
    db_conn.ping()
    try:
        student_info_query = """
            SELECT student_id, student_name, student_email, student_status, student_verify, student_indexnumber
            FROM Student
        """
        cursor = db_conn.cursor()
        cursor.execute(student_info_query)
        student_info_result = cursor.fetchall()
        result_list = []
        for row in student_info_result:
            result_list.append({
                'student_id': row[0],
                'student_name': row[1],
                'student_email': row[2],
                'student_status': row[3],
                'student_verify': row[4],
                'student_indexnumber': row[5]
            })
            print(result_list)
        return result_list
    except Exception as e:
        print(str(e))
        return jsonify({'error': 'An error has occurred'})
    finally:
        cursor.close()
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)