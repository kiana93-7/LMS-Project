from django.contrib import admin
from .models import Person, Student, Teacher, Course, StudentCourseTeacher,Certification, Education, CourseCategory, TeacherCertification



@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('PersianFirstName', 'PersianLastName', 'NationalCode', 'PhoneNumber', 'Sex', 'EducationID')
    search_fields = ('PersianFirstName', 'PersianLastName', 'NationalCode')
    list_filter = ('Sex', 'EducationID')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('PersonID', 'StudentCode', 'FatherName')
    search_fields = ('StudentCode', 'PersonID__PersianFirstName', 'PersonID__PersianLastName')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('PersonID', 'TeacherCode', 'MaritalStatus', 'Startdate')
    search_fields = ('PersonID__PersianFirstName', 'PersonID__PersianLastName', 'TeacherCode')
    list_filter = ('MaritalStatus',)


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('ID', 'CourseCategoryName', 'EnglishCourseCategoryName')
    search_fields = ('CourseCategoryName', 'EnglishCourseCategoryName')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('ID', 'CourseName', 'CourseCode', 'Duration', 'CourseType', 'CourseCategoryID')
    search_fields = ('CourseName', 'EnglishCourseName', 'CourseCode')
    list_filter = ('CourseType', 'CourseCategoryID')


@admin.register(StudentCourseTeacher)
class StudentCourseTeacherAdmin(admin.ModelAdmin):
    list_display = ('StudentID', 'CourseID', 'TeacherID', 'TermNumber', 'Score')
    search_fields = ('StudentID__PersonID__PersianFirstName', 'StudentID__PersonID__PersianLastName', 'CourseID__CourseName')
    list_filter = ('TermNumber', 'CourseID')


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('ID', 'CertificationTitle', 'Vendor', 'Startdate')
    search_fields = ('CertificationTitle', 'Vendor')


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('ID', 'EducationName')
    search_fields = ('EducationName',)


@admin.register(TeacherCertification)
class TeacherCertificationAdmin(admin.ModelAdmin):
    list_display = ('TeacherID', 'CertificationID', 'Score', 'Expiredate')
    search_fields = ('TeacherID__PersonID__PersianFirstName', 'CertificationID__CertificationTitle')