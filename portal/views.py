from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import *
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_datetime
from django.db import IntegrityError
import json
from django.db.models import Avg, Count
from collections import defaultdict
from decimal import Decimal


# Create your views here.
def index(request):
    return render(request, 'index.html')


def institution_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user:
            # Check if the user is associated with an institution
            try:
                institution = Institution.objects.get(user=user)
                login(request, user)
                return redirect('inst_page')  # Redirect to a dashboard or home page
            except Institution.DoesNotExist:
                messages.error(request, "No institution is associated with this user.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "institution_login.html")

def inst_page(request):
    inst = Institution.objects.get(user=request.user)
    context = {
        'inst': inst
    }
    return render(request, 'inst_page.html', context)

# Define a credit dictionary that maps course names to credit values
def dashboard(request):
    # GPA Distribution (Bar Chart)
    students = Student1.objects.all()
    gpa_data = [student.academic_records.aggregate(average_gpa=Avg('gpa'))['average_gpa'] for student in students]

    # Students Distribution by Category (Pie Chart)
    category_counts = Student1.objects.values('category').annotate(count=Count('category'))

    # Monthly Academic Record Entries (Line Chart)
    monthly_record_counts = AcademicRecord.objects.extra(select={'month': "EXTRACT(MONTH FROM date_entered)"}).values('month').annotate(count=Count('id')).order_by('month')

    # Prepare data for charts
    gpa_chart_data = {
        'labels': [student.name for student in students],
        'data': gpa_data
    }
    category_chart_data = {
        'labels': [category['category'] for category in category_counts],
        'data': [category['count'] for category in category_counts]
    }

    semesters = [1, 2, 3, 4, 5, 6, 7, 8]
    gpa_by_semester = []

    for semester in semesters:
        # Calculate the average GPA for the given semester
        avg_gpa = AcademicRecord.objects.filter(semester=semester).exclude(gpa__isnull=True).aggregate(Avg('gpa'))['gpa__avg']
        gpa_by_semester.append(avg_gpa if avg_gpa else 0)  # Use 0 if no data exists

    months = ["Jan", "Feb", "Mar", "Apr", "May"]
    attendance_rate = [90, 85, 80, 95, 88]

    # Create a textual report based on the data
    prompt = f"""
    Generate 4 paragraph containing a detailed report for the academic records of students.
    GPA distribution: {', '.join(map(str, gpa_data))}
    Students by Category: {', '.join(f'{category["category"]}: {category["count"]}' for category in category_counts)}
    GPA by Semester: {', '.join(map(str, gpa_by_semester))}
    Attendance Rate for each month: {', '.join(map(str, attendance_rate))}
    """

    context = {
        'gpa_chart_data': gpa_chart_data,
        'category_chart_data': category_chart_data,
        'semesters': json.dumps(semesters),
        'gpa_by_semester': json.dumps(gpa_by_semester),
        'months': months,
        'attendance_rate': attendance_rate,
    }

    return render(request, 'dashboard.html', context)


def financial_dashboard(request):
    # Fetch budgets, expenditures, and fundraising data
    budgets = Budget.objects.all()
    expenditures = Expenditure.objects.all()
    fundraising_events = Fundraising.objects.all()
    
    # Prepare data for charts
    budget_labels = [f"Year {budget.year}" for budget in budgets]
    budget_data = [budget.total_budget for budget in budgets]

    expenditure_data = [expenditure.amount_spent for expenditure in expenditures]
    expenditure_labels = [f"{expenditure.category} ({expenditure.date_spent.year})" for expenditure in expenditures]
    
    fundraising_data = [fundraising.amount_raised for fundraising in fundraising_events]
    fundraising_labels = [fundraising.fundraising_event for fundraising in fundraising_events]

    financial_summaries = FinancialSummary.objects.all()
    summary_data = [{
        'year': summary.budget.year,
        'net_balance': summary.total_fundraising - summary.total_expenditure
    } for summary in financial_summaries]

    context = {
        'budget_labels': budget_labels,
        'budget_data': budget_data,
        'expenditure_labels': expenditure_labels,
        'expenditure_data': expenditure_data,
        'fundraising_labels': fundraising_labels,
        'fundraising_data': fundraising_data,
        'summary_data': summary_data
    }

    return render(request, 'financial_dashboard.html', context)
@login_required
def manage_faculty(request):
    # Ensure the logged-in user is associated with an institution
    try:
        institution = Institution.objects.get(user=request.user)
    except Institution.DoesNotExist:
        messages.error(request, "You are not associated with any institution.")
        return redirect("dashboard")

    # Handle form submission for adding a faculty member
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        department = request.POST.get("department")

        if name and email and department:
            if Faculty.objects.filter(email=email).exists():
                messages.error(request, f"A faculty member with email '{email}' already exists.")
            else:
                Faculty.objects.create(
                    institution=institution, name=name, email=email, department=department
                )
                messages.success(request, f"Faculty member '{name}' added successfully!")
        else:
            messages.error(request, "All fields are required to add a faculty member.")

        return redirect("manage_faculty")

    # Retrieve all faculty members for this institution
    departments = Department.objects.filter(institution=institution)
    faculties = Faculty.objects.filter(institution=institution)

    context = {
        "faculties": faculties,
        "departments": departments,
    }
    return render(request, "manage_faculty.html", context)


@login_required
def delete_faculty(request, faculty_id):
    # Ensure the faculty belongs to the logged-in user's institution
    faculty = get_object_or_404(Faculty, id=faculty_id, institution__user=request.user)
    faculty.delete()
    messages.success(request, f"Faculty member '{faculty.name}' deleted successfully!")
    return redirect("manage_faculty")

@login_required
def manage_departments(request):
    # Ensure the logged-in user is associated with an institution
    try:
        institution = Institution.objects.get(user=request.user)
    except Institution.DoesNotExist:
        messages.error(request, "You are not associated with any institution.")
        return redirect("dashboard")

    # Handle form submission for adding a department
    if request.method == "POST":
        department_name = request.POST.get("name")

        if department_name:
            # Check if the department already exists for the institution
            if Department.objects.filter(name=department_name, institution=institution).exists():
                messages.error(request, f"The department '{department_name}' already exists.")
            else:
                Department.objects.create(institution=institution, name=department_name)
                messages.success(request, f"Department '{department_name}' created successfully!")
        else:
            messages.error(request, "Department name is required.")

        return redirect("manage_departments")

    # Retrieve all departments for this institution
    departments = Department.objects.filter(institution=institution)

    context = {
        "departments": departments,
    }
    return render(request, "manage_departments.html", context)

@login_required
def manage_hods(request):
    try:
        institution = Institution.objects.get(user=request.user)
    except Institution.DoesNotExist:
        messages.error(request, "You are not associated with an institution.")
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        department_id = request.POST.get("department")

        # Validation
        if not all([username, email, password, department_id]):
            messages.error(request, "All fields are required.")
            return redirect("manage_hods")

        try:
            department = Department.objects.get(id=department_id, institution=institution)
        except Department.DoesNotExist:
            messages.error(request, "Invalid department selected.")
            return redirect("manage_hods")

        if HoD.objects.filter(department=department).exists():
            messages.error(request, f"The department '{department.name}' already has an HoD.")
            return redirect("manage_hods")

        # Create User and HoD
        user = User.objects.create_user(username=username, email=email, password=password)
        HoD.objects.create(user=user, department=department)
        messages.success(request, f"HoD '{username}' created successfully for department '{department.name}'.")

        return redirect("manage_hods")

    # Fetch departments and existing HoDs
    departments = Department.objects.filter(institution=institution)
    hods = HoD.objects.filter(department__institution=institution)

    context = {
        "departments": departments,
        "hods": hods,
    }
    return render(request, "manage_hods.html", context)


def hod_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            try:
                hod = HoD.objects.get(user=user)  # Check if the user is an HoD
                login(request, user)
                return redirect("hod_dashboard")  # Redirect to HoD dashboard
            except HoD.DoesNotExist:
                messages.error(request, "You are not authorized to access the HoD dashboard.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "hod_login.html")

@login_required
def hod_dashboard(request):
    try:
        hod = HoD.objects.get(user=request.user)  # Ensure the logged-in user is an HoD
    except HoD.DoesNotExist:
        messages.error(request, "You do not have access to the HoD dashboard.")
        return redirect("hod_login")

    faculties = Faculty.objects.filter(department=hod.department)  # Faculty in the same department
    batches = Batch.objects.all()
    courses = Course.objects.filter(faculty__department=hod.department)

    if request.method == "POST":
        course_code = request.POST.get("course_code")
        course_name = request.POST.get("course_name")
        year = request.POST.get("year")
        faculty_id = request.POST.get("faculty")
        batch_id = request.POST.get("batch")

        if not (course_code and course_name and year and faculty_id and batch_id):
            messages.error(request, "Please fill in all fields.")
        else:
            faculty = Faculty.objects.get(id=faculty_id)
            batch = Batch.objects.get(id=batch_id)
            course = Course(
                course_code=course_code,
                course_name=course_name,
                year=year,
                faculty=faculty,
                batch=batch
            )
            course.save()
            messages.success(request, "Course added successfully!")
            return redirect("hod_dashboard")

    return render(request, "hod_dashboard.html", {
        "hod": hod,
        "faculties": faculties,
        "batches": batches,
        "courses": courses,
    })

@login_required
def add_student(request):
    if request.method == "POST":
        name = request.POST.get("name")
        reg_number = request.POST.get("reg_number")
        batch_id = request.POST.get("batch")
        gender = request.POST.get("gender")
        category = request.POST.get("category")
        address = request.POST.get("address")
        contact = request.POST.get("contact")

        if not (name and reg_number and batch_id and gender and category and address and contact):
            messages.error(request, "All fields are required.")
        else:
            try:
                batch = Batch.objects.get(id=batch_id)
                hod = HoD.objects.get(user=request.user)
                student = Student1(
                    name=name,
                    reg_number=reg_number,
                    admission_batch=batch,
                    gender=gender,
                    category=category,
                    address=address,
                    contact=contact,
                    department=hod.department
                )
                student.save()
                messages.success(request, f"Student {name} added successfully!")
                return redirect("add_student")
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")

    batches = Batch.objects.all()
    return render(request, "add_students.html", {"batches": batches})


@login_required
def select_student_semester(request):
    if request.method == "POST":
        student_id = request.POST.get("student")
        semester = request.POST.get("semester")
        
        if not student_id or not semester:
            messages.error(request, "Please select both a student and a semester.")
            return redirect("select_student_semester")

        # Redirect to the next step with selected student and semester
        return redirect("add_grades", student_id=student_id, semester=semester)
    
    # Get students based on the user's department if they are HoD
    try:
        hod = HoD.objects.get(user=request.user)
        students = Student1.objects.filter(department=hod.department)
    except:
        students = Student1.objects.all()

    return render(request, "select_student_semester.html", {
        "students": students,
        "semesters": AcademicRecord.SEMESTER_CHOICES,
    })

@login_required
def add_grades(request, student_id, semester):
    student = get_object_or_404(Student1, pk=student_id)
    year = (semester - 1) // 2 + 1
    dept = student.department
    if "Computer" in dept.name:
        courses = Course.objects.filter(course_code__startswith="CS", year=year)
    else:
        courses = Course.objects.filter(year=year)
    if request.method == "POST":
        errors = {}

        # Collect grades from POST data
        for course in courses:
            grade = request.POST.get(f"grade_{course.id}")
            if not grade:
                errors[course.course_code] = f"Grade for {course.course_name} is required."

        # Check if there are errors
        if errors:
            for error in errors.values():
                messages.error(request, error)
            return render(request, "add_grades.html", {"student": student, "semester": semester, "courses": courses})

        # Save each course's Academic Record
        for course in courses:
            grade = request.POST.get(f"grade_{course.id}")
            AcademicRecord.objects.create(
                student=student,
                semester=semester,
                course=course,
                grades={course.course_code: grade},
                created_by=request.user,
            )
        messages.success(request, "Academic records added successfully!")
        return redirect("select_student_semester")

    return render(request, "add_grades.html", {"student": student, "semester": semester, "courses": courses})

# List all achievements
def achievements_list(request):
    achievements = Achievement.objects.all().order_by('-date_awarded')
    return render(request, 'achievements_list.html', {'achievements': achievements})

# Add a new achievement (basic POST handling without forms.py)
def add_achievement(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        achievement_type = request.POST['achievement_type']
        awarded_to = request.POST['awarded_to']
        date_awarded = request.POST['date_awarded']
        image = request.FILES.get('image')

        Achievement.objects.create(
            title=title,
            description=description,
            achievement_type=achievement_type,
            awarded_to=awarded_to,
            date_awarded=date_awarded,
            image=image
        )
        return redirect('achievements_list')

    return render(request, 'add_achievement.html')