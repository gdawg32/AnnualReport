from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Institution(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)  # Link with User model
    name = models.CharField(max_length=255, unique=True)  # Unique institution name
    address = models.TextField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class Faculty(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="faculties")
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Department(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="departments")
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
    
class HoD(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    department = models.OneToOneField(Department, on_delete=models.CASCADE, related_name="hod")

    def __str__(self):
        return f"{self.user.username} - {self.department.name}"
    
class Batch(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Course(models.Model):
    course_code = models.CharField(max_length=20, unique=True)
    course_name = models.CharField(max_length=100)
    year = models.IntegerField()
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True)
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True)
    credit = models.PositiveSmallIntegerField(default=4)

    def __str__(self):
        return f"{self.course_name} ({self.course_code})"


class Student1(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=100)
    reg_number = models.CharField(max_length=20, unique=True)
    admission_batch = models.CharField(max_length=10)
    gender = models.CharField(max_length=10)
    category = models.CharField(max_length=20, choices=[('General', 'General'), ('OBC', 'OBC'), ('EWS', 'EWS'), ('SC', 'SC'), ('ST', 'ST')])
    address = models.TextField()
    contact = models.CharField(max_length=15)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="students", null=True, blank=True)

    def __str__(self):
        return self.name

    
class AcademicRecord(models.Model):
    SEMESTER_CHOICES = [
        (1, "Semester 1"),
        (2, "Semester 2"),
        (3, "Semester 3"),
        (4, "Semester 4"),
        (5, "Semester 5"),
        (6, "Semester 6"),
        (7, "Semester 7"),
        (8, "Semester 8"),
    ]

    student = models.ForeignKey(Student1, on_delete=models.CASCADE, related_name="academic_records")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="academic_records")
    semester = models.PositiveSmallIntegerField(choices=SEMESTER_CHOICES)
    grades = models.JSONField()  # Stores grades as a dictionary: {"subject_code": "grade"}
    gpa = models.FloatField(null=True, blank=True)  # GPA is calculated later
    credits_earned = models.PositiveSmallIntegerField(null=True, blank=True)  # Optional
    created_by = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True)  # HoD who entered the record
    date_entered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - Sem {self.semester}"

class Budget(models.Model):
    year = models.PositiveIntegerField()
    total_budget = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Budget for {self.year}"

class Expenditure(models.Model):
    budget = models.ForeignKey(Budget, related_name="expenditures", on_delete=models.CASCADE)
    category = models.CharField(max_length=255)
    amount_spent = models.DecimalField(max_digits=10, decimal_places=2)
    date_spent = models.DateField()
    description = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Expenditure of {self.amount_spent} on {self.category}"

class Fundraising(models.Model):
    year = models.PositiveIntegerField()
    amount_raised = models.DecimalField(max_digits=10, decimal_places=2)
    fundraising_event = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Fundraising of {self.amount_raised} in {self.year} ({self.fundraising_event})"

class FinancialSummary(models.Model):
    budget = models.ForeignKey(Budget, related_name="financial_summaries", on_delete=models.CASCADE)
    total_expenditure = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_fundraising = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def calculate_net_balance(self):
        # Calculate net balance = Total Fundraising - Total Expenditure
        self.net_balance = self.total_fundraising - self.total_expenditure
        self.save()

    def __str__(self):
        return f"Financial Summary for {self.budget.year}"
    
ACHIEVEMENT_TYPE_CHOICES = [
    ('Student', 'Student'),
    ('Faculty', 'Faculty'),
    ('Department', 'Department'),
]

class Achievement(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPE_CHOICES)
    awarded_to = models.CharField(max_length=200, help_text="Name of the recipient or department")
    date_awarded = models.DateField(default=now)
    image = models.ImageField(upload_to='achievements/', blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.achievement_type})"