from django.contrib import admin
from django.urls import path
from django.contrib.auth.decorators import user_passes_test
from lms_web import views


def is_superuser(user):
    return user.is_authenticated and user.is_superuser


admin.site.login = user_passes_test(is_superuser)(admin.site.login)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),

    path('courses/', views.course_list_view, name='course_list'),
    path('create-course/', views.course_create_view, name='course_create'),
    path('course/<int:pk>/', views.course_detail_view, name='course_detail'),
    path('course/<int:pk>/update/', views.course_update_view, name='course_update'),
    path('course/<int:pk>/delete/', views.course_delete_view, name='course_delete'),

    path('register-student/', views.student_register_view, name='student_register'),
    path('students/', views.student_list_view, name='student_list'),
    path('student/<int:pk>/update/', views.student_update_view, name='student_update'),
    path('student/<int:pk>/delete/', views.student_delete_view, name='student_delete'),

    path('create-teacher/', views.teacher_create_view, name='teacher_create'),
    path('teachers/', views.teacher_list_view, name='teacher_list'),
    path('teacher/<int:pk>/update/', views.teacher_update_view, name='teacher_update'),
    path('teacher/<int:pk>/delete/', views.teacher_delete_view, name='teacher_delete'),
    path('teacher/<int:pk>/detail/', views.teacher_detail_view, name='teacher_detail'),

    path('enroll/', views.enrollment_view, name='enrollment'),
    path('enrollments/', views.enrollment_list_view, name='enrollment_list'),
    path('enrollment/<int:pk>/delete/', views.enrollment_delete_view, name='enrollment_delete'),

    path('register-grade/', views.register_grade_view, name='register_grade'),

    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('create-certificate/', views.certificate_create_view, name='certificate_create'),

    path('api/student/<int:student_id>/course-info/', views.get_student_course_info, name='student_course_info'),

    path('calendar/', views.course_calendar_view, name='course_calendar'),

    path('categories/', views.category_list_view, name='category_list'),
    path('create-category/', views.category_create_view, name='category_create'),
    path('category/<int:pk>/update/', views.category_update_view, name='category_update'),
    path('category/<int:pk>/delete/', views.category_delete_view, name='category_delete'),

    path('enrollments/', views.enrollment_list_view, name='enrollment_list'),

    path('exams/', views.exam_list_view, name='exam_list'),
    path('exams/<int:course_id>/', views.exam_detail_view, name='exam_detail'),

    path('api/student-course-info/<int:student_id>/', views.get_student_course_info, name='get_student_course_info'),

    path('certificates/', views.certificate_list_view, name='certificate_list'),

    path('students/delete-all/', views.delete_all_students_view, name='delete_all_students'),

    path('exams/', views.exam_list_view, name='exam_list'),
    path('exams/<int:course_id>/', views.exam_detail_view, name='exam_detail'),
    path('exams/grade/<int:exam_id>/', views.exam_grade_view, name='exam_grade'),

    path('my-exams/', views.student_exams_view, name='student_exams'),

    path('certificates/<int:pk>/edit/', views.certificate_update_view, name='certificate_update'),
    path('certificates/<int:pk>/delete/', views.certificate_delete_view, name='certificate_delete'),

path('my-enrollments/', views.my_enrollments_view, name='my_enrollments'),
]