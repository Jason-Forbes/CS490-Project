from flask import Blueprint, render_template, request, jsonify, redirect, session
from app.authentication import supabase

main_bp = Blueprint('main', __name__)

@main_bp.route("/test")
def test():
    return "Flask is working!"

# Route for the home page
@main_bp.route("/")
def home():
    return render_template("signup.html")

@main_bp.route("/login")
def login_page():
    return render_template("login.html")

# ========= EMAIL/PASSWORD SIGNUP =========
@main_bp.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")
    role = data.get("role")
    
    print(f"Signing up: email={email}, role={role}, name={name}")

    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "data": {
                "full_name": name,
                "role": role
            }
        })

        print(f"Signup response: {response}")
        
        if response.user:
            print(f"User created with metadata: {response.user.user_metadata}")
            
            session['user_id'] = response.user.id
            session['role'] = role
            return jsonify({"success": True, "redirect": f"/{role}/dashboard"})
        else:
            return jsonify({"success": False, "message": "Sign-up failed. Please try again."})

    except Exception as e:
        print(f"Signup error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)})

# ========= EMAIL/PASSWORD LOGIN =========
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
            
            print(f"User metadata: {user_metadata}")
            print(f"Actual role: {actual_role}")
            print(f"Selected role: {selected_role}")
            
            if not actual_role:
                supabase.auth.update_user({
                    "data": {
                        "role": selected_role
                    }
                })
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
        print(f"Login error: {str(e)}")
        return jsonify({"success": False, "message": str(e)})

# ========= LOGOUT =========
@main_bp.route("/logout")
def logout():
    try:
        supabase.auth.sign_out()
        session.clear()
        return redirect('/')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ========= DASHBOARD ROUTES =========
@main_bp.route("/student/dashboard")
def student_dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template("student_view.html")

@main_bp.route("/instructor/dashboard")
def instructor_dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    # Team will add classes data here later
    return render_template("instructor_FrontEnd.html", classes={})

# ========= CLASS MANAGEMENT ROUTES (for team to build on) =========
@main_bp.route("/select_class", methods=["GET", "POST"])
def select_class():
    if request.method == "POST":
        class_id = request.form.get('class_id')
        session['selected_class'] = class_id
        return redirect('/instructor/dashboard')
    
    if 'role' in session:
        if session['role'] == 'student':
            return redirect('/student/dashboard')
        elif session['role'] == 'instructor':
            return redirect('/instructor/dashboard')
    return redirect('/login')

@main_bp.route("/add_class", methods=["POST"])
def add_class():
    if 'user_id' not in session or session.get('role') != 'instructor':
        return redirect('/login')
    
    # Team will implement database saving here
    name = request.form.get('name')
    number = request.form.get('number')
    semester = request.form.get('semester')
    start_date = request.form.get('start')
    end_date = request.form.get('end')
    days = request.form.get('days')
    
    print(f"Class to be added: {name}, {number}, {semester}")
    
    return redirect('/instructor/dashboard')