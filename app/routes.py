import csv
import io

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from app.authentication import supabase

main_bp = Blueprint('main', __name__)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def organize_by_learning_objectives(students):
    lo_dict = {}
    for student in students:
        for lo in student['learning_objectives']:
            lo_name = lo['name']
            if lo_name not in lo_dict:
                lo_dict[lo_name] = {
                    'name': lo_name,
                    'students_with_2m': [],
                    'students_with_1m': [],
                    'students_with_0m': [],
                    'total_students': len(students)
                }
            m_count = 0
            if lo['top_score'] == 'M':
                m_count += 1
            if lo['second_score'] == 'M':
                m_count += 1
            student_data = {
                'name': student['name'],
                'top_score': lo['top_score'],
                'second_score': lo['second_score']
            }
            if m_count == 2:
                lo_dict[lo_name]['students_with_2m'].append(student_data)
            elif m_count == 1:
                lo_dict[lo_name]['students_with_1m'].append(student_data)
            else:
                lo_dict[lo_name]['students_with_0m'].append(student_data)
    
    learning_objectives = []
    for lo_name, lo_data in lo_dict.items():
        lo_data['two_m_count'] = len(lo_data['students_with_2m'])
        lo_data['one_m_count'] = len(lo_data['students_with_1m'])
        lo_data['zero_m_count'] = len(lo_data['students_with_0m'])
        learning_objectives.append(lo_data)
    return learning_objectives

# ============================================================================
# PAGE ROUTES
# ============================================================================

@main_bp.route("/")
def home():
    return render_template("signup.html")

@main_bp.route("/login")
def login_page():
    return render_template("login.html")

@main_bp.route("/logout")
def logout():
    try:
        supabase.auth.sign_out()
        session.clear()
        return redirect('/')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================================
# DASHBOARD ROUTES
# ============================================================================

@main_bp.route("/student/dashboard")
def student_dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template("student_view.html")

@main_bp.route("/instructor/dashboard")
def instructor_dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    
    # Get classes for this instructor from Supabase
    result = supabase.table('classes').select('*').eq('instructor_id', session['user_id']).execute()
    
    # Convert to dictionary format that template expects
    classes_dict = {}
    for c in result.data:
        classes_dict[str(c['id'])] = c
    
    return render_template("instructor_FrontEnd.html", classes=classes_dict)

# ============================================================================
# CLASS ROUTES
# ============================================================================

@main_bp.route("/class/<class_id>")
def class_detail(class_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    # Get class from Supabase
    class_result = supabase.table('classes').select('*').eq('id', class_id).execute()
    
    if not class_result.data:
        return redirect(url_for('main.instructor_dashboard'))
    
    class_data = class_result.data[0]
    
    # Get students for this class
    students_result = supabase.table('students').select('*').eq('class_id', class_id).execute()
    
    # Build students list with their grades
    students = []
    for student in students_result.data:
        # Get grades for this student
        grades_result = supabase.table('grades').select('*, learning_objectives(name)').eq('student_id', student['id']).execute()
        
        student_los = []
        for grade in grades_result.data:
            student_los.append({
                'name': grade['learning_objectives']['name'],
                'top_score': grade['top_score'] or 'X',
                'second_score': grade['second_score'] or 'X'
            })
        
        students.append({
            'id': student['id'],
            'name': student['name'],
            'learning_objectives': student_los
        })
    
    learning_objectives = organize_by_learning_objectives(students)
    
    return render_template('class_detail.html',
                         class_id=class_id,
                         class_name=class_data['name'],
                         students=students,
                         learning_objectives=learning_objectives)

@main_bp.route("/select_class", methods=['POST'])
def select_class():
    class_id = request.form.get('class_id')
    if class_id:
        # Verify class exists in Supabase
        result = supabase.table('classes').select('id').eq('id', class_id).execute()
        if result.data:
            return redirect(url_for('main.class_detail', class_id=class_id))
    return redirect(url_for('main.instructor_dashboard'))

@main_bp.route("/class/<class_id>/create_learning_objective")
def create_learning_objective(class_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    # Verify class exists
    class_result = supabase.table('classes').select('*').eq('id', class_id).execute()
    if not class_result.data:
        return redirect(url_for('main.instructor_dashboard'))
    
    class_data = class_result.data[0]
    return render_template('create_learning_objective.html',
                         class_id=class_id,
                         class_name=class_data['name'])

@main_bp.route("/class/<class_id>/update_grade")
def update_grade(class_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    # Verify class exists
    class_result = supabase.table('classes').select('*').eq('id', class_id).execute()
    if not class_result.data:
        return redirect(url_for('main.instructor_dashboard'))
    
    class_data = class_result.data[0]
    return render_template('update_grade.html',
                         class_id=class_id,
                         class_name=class_data['name'])

@main_bp.route("/class/<class_id>/upload_grades", methods=['POST'])
def upload_grades(class_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    # Verify class exists
    class_result = supabase.table('classes').select('id').eq('id', class_id).execute()
    if not class_result.data:
        return redirect(url_for('main.instructor_dashboard'))
    
    if 'file' not in request.files:
        return "No file uploaded", 400
    file = request.files['file']
    if file.filename == '':
        return "No file selected", 400
    
    # Read CSV file
    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    csv_reader = csv.DictReader(stream)
    
    for row in csv_reader:
        student_number = row.get('student_number')
        student_name = row.get('student_name')
        
        # Find or create student
        student_result = supabase.table('students').select('id').eq('class_id', class_id).eq('student_number', student_number).execute()
        
        if student_result.data:
            student_id = student_result.data[0]['id']
        else:
            # Create new student
            new_student = supabase.table('students').insert({
                'class_id': class_id,
                'name': student_name,
                'student_number': student_number
            }).execute()
            student_id = new_student.data[0]['id']
        
        # Process each LO column (LO1_top, LO1_second, LO2_top, etc.)
        lo_numbers = set()
        for key in row.keys():
            if key and key.startswith('LO') and '_' in key:  # Added check for key not None
                lo_num = key.split('_')[0]  # e.g., "LO1"
                lo_numbers.add(lo_num)
        
        for lo_num in lo_numbers:
            top_score = row.get(f'{lo_num}_top')
            second_score = row.get(f'{lo_num}_second')
            
            # Find learning objective
            lo_result = supabase.table('learning_objectives').select('id').eq('class_id', class_id).eq('name', lo_num).execute()
            
            if lo_result.data:
                lo_id = lo_result.data[0]['id']
                
                # Update or insert grade
                existing_grade = supabase.table('grades').select('id').eq('student_id', student_id).eq('learning_objective_id', lo_id).execute()
                
                if existing_grade.data:
                    # Update existing grade
                    supabase.table('grades').update({
                        'top_score': top_score,
                        'second_score': second_score
                    }).eq('id', existing_grade.data[0]['id']).execute()
                else:
                    # Insert new grade
                    supabase.table('grades').insert({
                        'student_id': student_id,
                        'learning_objective_id': lo_id,
                        'top_score': top_score,
                        'second_score': second_score
                    }).execute()
    
    return redirect(url_for('main.class_detail', class_id=class_id))

@main_bp.route("/class/<class_id>/upload_learning_objective", methods=['POST'])
def upload_learning_objective(class_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    # Verify class exists
    class_result = supabase.table('classes').select('id').eq('id', class_id).execute()
    if not class_result.data:
        return redirect(url_for('main.instructor_dashboard'))
    
    if 'file' not in request.files:
        return "No file uploaded", 400
    file = request.files['file']
    if file.filename == '':
        return "No file selected", 400
    
    # Read CSV file
    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    csv_reader = csv.DictReader(stream)
    
    # Get LO names from CSV headers
    headers = csv_reader.fieldnames
    lo_names = []
    for header in headers:
        if header and header.startswith('LO') and '_top' in header:  # Added check for header not None
            lo_name = header.split('_')[0]  # e.g., "LO1"
            if lo_name not in lo_names:
                lo_names.append(lo_name)
    
    # Create learning objectives
    for lo_name in lo_names:
        # Check if LO already exists
        existing = supabase.table('learning_objectives').select('id').eq('class_id', class_id).eq('name', lo_name).execute()
        
        if not existing.data:
            supabase.table('learning_objectives').insert({
                'class_id': class_id,
                'name': lo_name
            }).execute()
    
    return redirect(url_for('main.class_detail', class_id=class_id))

@main_bp.route("/add_class", methods=['POST'])
def add_class():
    if 'user_id' not in session or session.get('role') != 'instructor':
        return redirect('/login')
    
    name = request.form.get('name')
    number = request.form.get('number')
    semester = request.form.get('semester')
    start = request.form.get('start')
    end = request.form.get('end')
    days = request.form.get('days')
    
    # Insert into Supabase
    new_class = {
        'instructor_id': session['user_id'],
        'name': f'{semester} - {number} - {name}',
        'semester': semester,
        'start_date': start if start else None,
        'end_date': end if end else None,
        'days': days
    }
    
    result = supabase.table('classes').insert(new_class).execute()
    new_id = result.data[0]['id']
    
    return redirect(url_for('main.class_detail', class_id=new_id))

# ============================================================================
# API ROUTES - Authentication
# ============================================================================

@main_bp.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")
    role = data.get("role")
    
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "data": {
                "full_name": name,
                "role": role
            }
        })
        
        if response.user:
            session['user_id'] = response.user.id
            session['role'] = role
            return jsonify({"success": True, "redirect": f"/{role}/dashboard"})
        else:
            return jsonify({"success": False, "message": "Sign-up failed. Please try again."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@main_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    selected_role = data.get("role")

    try:
        result = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if result.user:
            user_metadata = result.user.user_metadata or {}
            actual_role = user_metadata.get('role')
            
            if not actual_role:
                supabase.auth.update_user({"data": {"role": selected_role}})
                actual_role = selected_role
            
            if actual_role != selected_role:
                return jsonify({
                    "success": False, 
                    "message": f"This account is registered as a {actual_role}, not a {selected_role}"
                })
            
            session['user_id'] = result.user.id
            session['role'] = actual_role
            return jsonify({"success": True, "redirect": f"/{actual_role}/dashboard"})
        else:
            return jsonify({"success": False, "message": "Invalid credentials"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@main_bp.route("/api/search", methods=['GET'])
def search():
    query = request.args.get('query', '').lower()
    view = request.args.get('view', 'students')
    class_id = request.args.get('class_id')
    
    # Get class data from Supabase
    class_result = supabase.table('classes').select('id').eq('id', class_id).execute()
    if not class_result.data:
        return jsonify({'error': 'Class not found'}), 404
    
    # Get students for this class
    students_result = supabase.table('students').select('*').eq('class_id', class_id).execute()
    
    # Build students list with their grades
    students = []
    for student in students_result.data:
        grades_result = supabase.table('grades').select('*, learning_objectives(name)').eq('student_id', student['id']).execute()
        
        student_los = []
        for grade in grades_result.data:
            student_los.append({
                'name': grade['learning_objectives']['name'],
                'top_score': grade['top_score'] or 'X',
                'second_score': grade['second_score'] or 'X'
            })
        
        students.append({
            'id': student['id'],
            'name': student['name'],
            'learning_objectives': student_los
        })
    
    if view == 'students':
        filtered_students = [
            student for student in students
            if query in student['name'].lower()
        ]
        return jsonify({'students': filtered_students})
    else:
        learning_objectives = organize_by_learning_objectives(students)
        filtered_los = []
        for lo in learning_objectives:
            if query in lo['name'].lower():
                filtered_los.append(lo)
            else:
                matching_2m = [s for s in lo['students_with_2m'] if query in s['name'].lower()]
                matching_1m = [s for s in lo['students_with_1m'] if query in s['name'].lower()]
                matching_0m = [s for s in lo['students_with_0m'] if query in s['name'].lower()]
                if matching_2m or matching_1m or matching_0m:
                    filtered_lo = lo.copy()
                    filtered_lo['students_with_2m'] = matching_2m
                    filtered_lo['students_with_1m'] = matching_1m
                    filtered_lo['students_with_0m'] = matching_0m
                    filtered_lo['two_m_count'] = len(matching_2m)
                    filtered_lo['one_m_count'] = len(matching_1m)
                    filtered_lo['zero_m_count'] = len(matching_0m)
                    filtered_los.append(filtered_lo)
        return jsonify({'learning_objectives': filtered_los})