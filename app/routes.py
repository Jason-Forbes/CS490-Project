# app/routes.py

# This file defines the URL routes (pages) for our Flask app.
# Each route is connected to a Python function that tells Flask
# what HTML template to render when someone visits that URL.
from flask import Blueprint, render_template, request, redirect, url_for, jsonify


# Create a Blueprint named 'main'.
# A Blueprint is a way to organize routes so we can keep our app modular and clean.
# Think of it as a group of related pages.
main_bp = Blueprint('main', __name__)


# ============================================================================
# SAMPLE DATA - Replace this with database queries later
# ============================================================================

# Sample classes data structure
classes = {
    '1': {
        'id': '1',
        'name': 'Fall 2025 - Math 211 - Section 2',
        'semester': 'Fall 2025',
        'students': [
            {
                'id': '1',
                'name': 'Adams, John',
                'learning_objectives': [
                    {'name': 'Learning Objective 1', 'top_score': 'M', 'second_score': 'M'},
                    {'name': 'Learning Objective 2', 'top_score': 'M', 'second_score': 'M'},
                    {'name': 'Learning Objective 3', 'top_score': 'M', 'second_score': 'M'},
                    {'name': 'Learning Objective 4', 'top_score': 'M', 'second_score': 'M'},
                    {'name': 'Learning Objective 5', 'top_score': 'M', 'second_score': 'M'},
                ]
            },
            {
                'id': '2',
                'name': 'Basic, Anna',
                'learning_objectives': [
                    {'name': 'Learning Objective 1', 'top_score': 'M', 'second_score': 'M'},
                    {'name': 'Learning Objective 2', 'top_score': 'M', 'second_score': 'M'},
                    {'name': 'Learning Objective 3', 'top_score': 'M', 'second_score': 'M'},
                    {'name': 'Learning Objective 4', 'top_score': 'M', 'second_score': 'M'},
                    {'name': 'Learning Objective 5', 'top_score': 'M', 'second_score': 'M'},
                ]
            },
            {
                'id': '3',
                'name': 'Smith, George W.',
                'learning_objectives': [
                    {'name': 'Learning Objective 1', 'top_score': 'M', 'second_score': 'R'},
                    {'name': 'Learning Objective 2', 'top_score': 'M', 'second_score': 'R'},
                    {'name': 'Learning Objective 3', 'top_score': 'R', 'second_score': 'X'},
                    {'name': 'Learning Objective 4', 'top_score': 'R', 'second_score': 'X'},
                    {'name': 'Learning Objective 5', 'top_score': 'M', 'second_score': 'M'},
                ]
            },
            {
                'id': '4',
                'name': 'Tucker, Cameron',
                'learning_objectives': [
                    {'name': 'Learning Objective 1', 'top_score': 'R', 'second_score': 'X'},
                    {'name': 'Learning Objective 2', 'top_score': 'M', 'second_score': 'M'},
                    {'name': 'Learning Objective 3', 'top_score': 'M', 'second_score': 'M'},
                    {'name': 'Learning Objective 4', 'top_score': 'M', 'second_score': 'R'},
                    {'name': 'Learning Objective 5', 'top_score': 'R', 'second_score': 'X'},
                ]
            },
        ]
    },
    '2': {
        'id': '2',
        'name': 'Fall 2025 - Math 101 - Section 1',
        'semester': 'Fall 2025',
        'students': [
            {
                'id': '5',
                'name': 'Johnson, Emily',
                'learning_objectives': [
                    {'name': 'Learning Objective 1', 'top_score': 'M', 'second_score': 'M'},
                    {'name': 'Learning Objective 2', 'top_score': 'M', 'second_score': 'R'},
                    {'name': 'Learning Objective 3', 'top_score': 'R', 'second_score': 'R'},
                ]
            },
            {
                'id': '6',
                'name': 'Williams, Michael',
                'learning_objectives': [
                    {'name': 'Learning Objective 1', 'top_score': 'M', 'second_score': 'M'},
                    {'name': 'Learning Objective 2', 'top_score': 'M', 'second_score': 'M'},
                    {'name': 'Learning Objective 3', 'top_score': 'M', 'second_score': 'M'},
                ]
            },
        ]
    }
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def organize_by_learning_objectives(students):
    """
    Organize student data by learning objectives with mastery levels.
    
    This function takes a list of students and reorganizes the data
    so it's grouped by learning objective instead of by student.
    Each LO shows students grouped by mastery level (2M, 1M, 0M).
    
    Args:
        students: List of student dictionaries with learning_objectives
        
    Returns:
        List of learning objectives with students grouped by mastery level
    """
    lo_dict = {}
    
    # Collect all learning objectives
    for student in students:
        for lo in student['learning_objectives']:
            lo_name = lo['name']
            
            # Initialize this learning objective if we haven't seen it yet
            if lo_name not in lo_dict:
                lo_dict[lo_name] = {
                    'name': lo_name,
                    'students_with_2m': [],
                    'students_with_1m': [],
                    'students_with_0m': [],
                    'total_students': len(students)
                }
            
            # Count how many M's this student has for this LO
            m_count = 0
            if lo['top_score'] == 'M':
                m_count += 1
            if lo['second_score'] == 'M':
                m_count += 1
            
            # Create student data object
            student_data = {
                'name': student['name'],
                'top_score': lo['top_score'],
                'second_score': lo['second_score']
            }
            
            # Add student to appropriate mastery group
            if m_count == 2:
                lo_dict[lo_name]['students_with_2m'].append(student_data)
            elif m_count == 1:
                lo_dict[lo_name]['students_with_1m'].append(student_data)
            else:
                lo_dict[lo_name]['students_with_0m'].append(student_data)
    
    # Convert dictionary to list and add counts
    learning_objectives = []
    for lo_name, lo_data in lo_dict.items():
        lo_data['two_m_count'] = len(lo_data['students_with_2m'])
        lo_data['one_m_count'] = len(lo_data['students_with_1m'])
        lo_data['zero_m_count'] = len(lo_data['students_with_0m'])
        learning_objectives.append(lo_data)
    
    return learning_objectives


# ============================================================================
# ROUTES
# ============================================================================

# Route for the home page ("/")
@main_bp.route("/")
def home():
    """Landing page - can redirect to instructor main or login"""
    return render_template("instructor_FrontEnd.html", classes=classes)


@main_bp.route("/instructor")
def instructor_main():
    """Instructor main page - choose or add a class"""
    return render_template("instructor_FrontEnd.html", classes=classes)


@main_bp.route("/class/<class_id>")
def class_detail(class_id):
    """
    Class detail page showing students and learning objectives.
    
    This page has two views:
    1. By Students - expandable list of students showing their LO scores
    2. By Learning Objectives - expandable list of LOs showing students grouped by mastery
    
    Args:
        class_id: The ID of the class to display
    """
    # Check if class exists
    if class_id not in classes:
        # If class doesn't exist, redirect back to instructor main page
        return redirect(url_for('main.instructor_main'))
    
    # Get class data
    class_data = classes[class_id]
    students = class_data['students']
    
    # Organize data by learning objectives (for the "By Learning Objectives" view)
    learning_objectives = organize_by_learning_objectives(students)
    
    # Render the template with both data structures
    return render_template('class_detail.html',
                         class_id=class_id,  # <-- IMPORTANT: Pass class_id to template
                         class_name=class_data['name'],
                         students=students,
                         learning_objectives=learning_objectives)


@main_bp.route("/select_class", methods=['POST'])
def select_class():
    """
    Handle form submission when selecting an existing class.
    Redirects to the class detail page.
    """
    class_id = request.form.get('class_id')
    
    if class_id and class_id in classes:
        return redirect(url_for('main.class_detail', class_id=class_id))
    else:
        # If invalid class ID, redirect back to instructor main
        return redirect(url_for('main.instructor_main'))


@main_bp.route("/class/<class_id>/create_learning_objective")
def create_learning_objective(class_id):
    """Page to create a new learning objective"""
    # Check if class exists
    if class_id not in classes:
        return redirect(url_for('main.instructor_main'))
    
    class_data = classes[class_id]
    
    return render_template('create_learning_objective.html',
                         class_id=class_id,
                         class_name=class_data['name'])


@main_bp.route("/class/<class_id>/update_grade")
def update_grade(class_id):
    """Page to update student grades"""
    # Check if class exists
    if class_id not in classes:
        return redirect(url_for('main.instructor_main'))
    
    class_data = classes[class_id]
    
    return render_template('update_grade.html',
                         class_id=class_id,
                         class_name=class_data['name'])


@main_bp.route("/class/<class_id>/upload_grades", methods=['POST'])
def upload_grades(class_id):
    """Handle grade file upload"""
    # Check if class exists
    if class_id not in classes:
        return redirect(url_for('main.instructor_main'))
    
    # Check if file was uploaded
    if 'file' not in request.files:
        return "No file uploaded", 400
    
    file = request.files['file']
    
    if file.filename == '':
        return "No file selected", 400
    
    # TODO: Process the uploaded file (CSV/Excel)
    # For now, just redirect back to class detail
    # Later you'll add code here to parse the file and update grades
    
    return redirect(url_for('main.class_detail', class_id=class_id))


@main_bp.route("/class/<class_id>/upload_learning_objective", methods=['POST'])
def upload_learning_objective(class_id):
    """Handle learning objective file upload"""
    # Check if class exists
    if class_id not in classes:
        return redirect(url_for('main.instructor_main'))
    
    # Check if file was uploaded
    if 'file' not in request.files:
        return "No file uploaded", 400
    
    file = request.files['file']
    
    if file.filename == '':
        return "No file selected", 400
    
    # TODO: Process the uploaded file (CSV/Excel)
    # For now, just redirect back to class detail
    # Later you'll add code here to parse the file and create the learning objective
    
    return redirect(url_for('main.class_detail', class_id=class_id))


@main_bp.route("/add_class", methods=['POST'])
def add_class():
    """
    Handle form submission to add a new class.
    
    Expects form data with:
    - name: Section name or number
    - number: Class number
    - semester: Semester (e.g., "Fall 2025")
    - start: Start date
    - end: End date
    - days: Class days (e.g., "MW")
    """
    name = request.form.get('name')
    number = request.form.get('number')
    semester = request.form.get('semester')
    start = request.form.get('start')
    end = request.form.get('end')
    days = request.form.get('days')
    
    # Generate a new class ID
    new_id = str(len(classes) + 1)
    
    # Create new class in our data structure
    classes[new_id] = {
        'id': new_id,
        'name': f'{semester} - {number} - {name}',
        'semester': semester,
        'start_date': start,
        'end_date': end,
        'days': days,
        'students': []  # Start with no students
    }
    
    # Redirect to the new class detail page
    return redirect(url_for('main.class_detail', class_id=new_id))


# ============================================================================
# API ENDPOINTS (Optional - for server-side search)
# ============================================================================

@main_bp.route("/api/search", methods=['GET'])
def search():
    """
    API endpoint for search functionality.
    
    This is optional - the current implementation uses client-side search (JavaScript).
    You can use this if you want to move search logic to the server.
    
    Query parameters:
    - query: Search term
    - view: 'students' or 'objectives'
    - class_id: ID of the class to search in
    """
    query = request.args.get('query', '').lower()
    view = request.args.get('view', 'students')
    class_id = request.args.get('class_id', '1')
    
    # Check if class exists
    if class_id not in classes:
        return jsonify({'error': 'Class not found'}), 404
    
    class_data = classes[class_id]
    
    if view == 'students':
        # Filter students by name
        filtered_students = [
            student for student in class_data['students']
            if query in student['name'].lower()
        ]
        return jsonify({'students': filtered_students})
    
    else:  # view == 'objectives'
        # Filter by learning objective name or student name
        learning_objectives = organize_by_learning_objectives(class_data['students'])
        filtered_los = []
        
        for lo in learning_objectives:
            # Check if LO name matches
            if query in lo['name'].lower():
                filtered_los.append(lo)
            else:
                # Check if any student name matches
                matching_2m = [s for s in lo['students_with_2m'] if query in s['name'].lower()]
                matching_1m = [s for s in lo['students_with_1m'] if query in s['name'].lower()]
                matching_0m = [s for s in lo['students_with_0m'] if query in s['name'].lower()]
                
                # Only include this LO if we found matching students
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