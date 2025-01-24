from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("institution-login/", views.institution_login, name="institution_login"),
    path('inst-page/', views.inst_page, name='inst_page'),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("manage-faculty/", views.manage_faculty, name="manage_faculty"),
    path("delete-faculty/<int:faculty_id>/", views.delete_faculty, name="delete_faculty"),
    path("manage-departments/", views.manage_departments, name="manage_departments"),
    path("manage-hods/", views.manage_hods, name="manage_hods"),
    path("hod-dashboard/", views.hod_dashboard, name="hod_dashboard"),
    path("hod-login/", views.hod_login, name="hod_login"),
    path("add-student/", views.add_student, name="add_student"),
    path("select-student-semester/", views.select_student_semester, name="select_student_semester"),
    path("add-grades/<int:student_id>/<int:semester>/", views.add_grades, name="add_grades"),
    path('financial-dashboard/', views.financial_dashboard, name='financial_dashboard'),
    path('achievements/', views.achievements_list, name='achievements_list'),
    path('achievements/add/', views.add_achievement, name='add_achievement'),


    
]