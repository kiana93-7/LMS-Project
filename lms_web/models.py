from django.db import models

class Education(models.Model):
    ID = models.AutoField(primary_key=True, db_column='ID')
    EducationName = models.CharField(max_length=40, db_column='EducationName', verbose_name="نام مدرک")

    class Meta:
        managed = True
        db_table = 'Education'
        verbose_name = "مدرک تحصیلی"
        verbose_name_plural = "مدارک تحصیلی"

    def __str__(self):
        return self.EducationName

class Department(models.Model):
    ID = models.AutoField(primary_key=True, db_column='ID')
    DepartmentName = models.CharField(max_length=40, db_column='DepartmentName', verbose_name="نام دپارتمان")

    class Meta:
        managed = True
        db_table = 'Department'
        verbose_name = "دپارتمان"
        verbose_name_plural = "دپارتمان‌ها"

    def __str__(self):
        return self.DepartmentName

class Job(models.Model):
    ID = models.AutoField(primary_key=True, db_column='ID')
    JobTitle = models.CharField(max_length=60, db_column='JobTitle', verbose_name="عنوان شغل")

    class Meta:
        managed = True
        db_table = 'Job'
        verbose_name = "شغل"
        verbose_name_plural = "شغل‌ها"

    def __str__(self):
        return self.JobTitle

class Person(models.Model):
    ID = models.AutoField(primary_key=True, db_column='ID')
    PersianFirstName = models.CharField(max_length=60, db_column='PersianFirstName', verbose_name="نام (فارسی)")
    EnglishFirstName = models.CharField(max_length=20, db_column='EnglishFirstName', verbose_name="نام (انگلیسی)", blank=True, null=True)
    PersianLastName = models.CharField(max_length=100, db_column='PersianLastName', verbose_name="نام خانوادگی (فارسی)")
    EnglishLastName = models.CharField(max_length=30, db_column='EnglishLastName', verbose_name="نام خانوادگی (انگلیسی)", blank=True, null=True)
    NationalCode = models.CharField(max_length=20, db_column='NationalCode', verbose_name="کد ملی", unique=True)
    Sex = models.CharField(max_length=20, db_column='Sex', verbose_name="جنسیت")
    Birthdate = models.DateField(db_column='Birthdate', verbose_name="تاریخ تولد", null=True, blank=True)
    HomeAddress = models.CharField(max_length=400, db_column='HomeAddress', verbose_name="آدرس منزل", blank=True, null=True)
    PhoneNumber = models.CharField(max_length=11, db_column='PhoneNumber', verbose_name="شماره تماس", blank=True, null=True)
    EmailAddress = models.CharField(max_length=100, db_column='EmailAddress', verbose_name="ایمیل", blank=True, null=True)
    EducationID = models.ForeignKey(Education, on_delete=models.SET_NULL, null=True, db_column='EducationID', verbose_name="مدرک تحصیلی")

    class Meta:
        managed = True
        db_table = 'Person'
        verbose_name = "شخص"
        verbose_name_plural = "اشخاص"

    def __str__(self):
        return f"{self.PersianFirstName} {self.PersianLastName}"

class Student(models.Model):
    PersonID = models.OneToOneField(Person, on_delete=models.CASCADE, primary_key=True, db_column='PersonID')
    StudentCode = models.IntegerField(db_column='StudentCode', verbose_name="شماره دانشجویی", unique=True)
    FatherName = models.CharField(max_length=40, db_column='FatherName', verbose_name="نام پدر")
    WorkAddress = models.CharField(max_length=400, db_column='WorkAddress', verbose_name="آدرس محل کار", blank=True, null=True)
    WorkPhone = models.CharField(max_length=15, db_column='WorkPhone', verbose_name="تلفن محل کار", blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Student'
        verbose_name = "دانشجو"
        verbose_name_plural = "دانشجویان"

    def __str__(self):
        return f"{self.PersonID.PersianFirstName} {self.PersonID.PersianLastName}"

class Teacher(models.Model):
    PersonID = models.OneToOneField(Person, on_delete=models.CASCADE, primary_key=True, db_column='PersonID')
    TeacherCode = models.IntegerField(db_column='TeacherCode', verbose_name="کد استاد", unique=True)
    MaritalStatus = models.CharField(max_length=40, db_column='MaritalStatus', verbose_name="وضعیت تاهل")
    Startdate = models.DateField(db_column='Startdate', verbose_name="تاریخ شروع")
    InsuranceNumber = models.CharField(max_length=10, db_column='InsuranceNumber', verbose_name="شماره بیمه", blank=True, null=True)
    AccountNumber = models.CharField(max_length=16, db_column='AccountNumber', verbose_name="شماره حساب", blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Teacher'
        verbose_name = "استاد"
        verbose_name_plural = "اساتید"

    def __str__(self):
        return f"{self.PersonID.PersianFirstName} {self.PersonID.PersianLastName}"

class CourseCategory(models.Model):
    ID = models.AutoField(primary_key=True, db_column='ID')
    CourseCategoryName = models.CharField(max_length=100, db_column='CourseCategoryName', verbose_name="نام دسته‌بندی")
    EnglishCourseCategoryName = models.CharField(max_length=50, db_column='EnglishCourseCategoryName', verbose_name="نام دسته‌بندی (انگلیسی)")

    class Meta:
        managed = True
        db_table = 'CourseCategory'
        verbose_name = "دسته‌بندی دوره"
        verbose_name_plural = "دسته‌بندی دوره‌ها"

    def __str__(self):
        return self.CourseCategoryName

class Course(models.Model):
    ID = models.SmallAutoField(primary_key=True, db_column='ID')
    CourseCode = models.IntegerField(db_column='CourseCode', verbose_name="کد دوره")
    CourseName = models.CharField(max_length=100, db_column='CourseName', verbose_name="نام دوره")
    EnglishCourseName = models.CharField(max_length=50, db_column='EnglishCourseName', verbose_name="نام دوره (انگلیسی)")
    Duration = models.SmallIntegerField(db_column='Duration', verbose_name="مدت (ساعت)")
    CourseType = models.CharField(max_length=40, db_column='CourseType', verbose_name="نوع دوره")
    Description = models.TextField(db_column='Description', verbose_name="توضیحات")
    Syllabus = models.TextField(db_column='Syllabus', verbose_name="سرفصل‌ها")
    SyllabusFile = models.BinaryField(null=True, blank=True, db_column='SyllabusFile', verbose_name="فایل سرفصل‌ها")
    CourseCategoryID = models.ForeignKey(CourseCategory, on_delete=models.DO_NOTHING, db_column='CourseCategoryID', verbose_name="دسته‌بندی")
    TeacherID = models.ForeignKey(Teacher, on_delete=models.DO_NOTHING, null=True, blank=True, db_column='TeacherID', verbose_name="استاد")

    class Meta:
        managed = True
        db_table = 'Course'
        ordering = ['ID']
        verbose_name = "دوره"
        verbose_name_plural = "دوره‌ها"

    def __str__(self):
        return self.CourseName

class Certification(models.Model):
    ID = models.SmallAutoField(primary_key=True, db_column='ID')
    CertificationTitle = models.CharField(max_length=70, db_column='CertificationTitle', verbose_name="عنوان مدرک")
    Vendor = models.CharField(max_length=50, db_column='Vendor', verbose_name="صادرکننده")
    Startdate = models.DateField(db_column='Startdate', verbose_name="تاریخ صدور", null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'Certification'
        verbose_name = "مدرک"
        verbose_name_plural = "مدارک"

    def __str__(self):
        return self.CertificationTitle

class TeacherCertification(models.Model):
    TeacherID = models.ForeignKey(Teacher, on_delete=models.CASCADE, db_column='TeacherID')
    CertificationID = models.ForeignKey(Certification, on_delete=models.CASCADE, db_column='CertificationID')
    Score = models.SmallIntegerField(db_column='Score', verbose_name="نمره")
    Expiredate = models.DateField(db_column='Expiredate', verbose_name="تاریخ انقضا", null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'Teacher_Certification'
        unique_together = ('TeacherID', 'CertificationID')

class StudentCourseTeacher(models.Model):
    StudentID = models.ForeignKey(Student, on_delete=models.CASCADE, db_column='StudentID')
    CourseID = models.ForeignKey(Course, on_delete=models.CASCADE, db_column='CourseID')
    TeacherID = models.ForeignKey(Teacher, on_delete=models.CASCADE, db_column='TeacherID')
    TermNumber = models.IntegerField(db_column='TermNumber', verbose_name="شماره ترم")
    Score = models.SmallIntegerField(db_column='Score', verbose_name="نمره")

    class Meta:
        managed = True
        db_table = 'Student_Course_Teacher'
        unique_together = ('StudentID', 'CourseID', 'TeacherID', 'TermNumber')

class Exam(models.Model):
    Course = models.ForeignKey(Course, on_delete=models.CASCADE, db_column='Course_id', to_field='ID', verbose_name="دوره")
    Title = models.CharField(max_length=100, verbose_name="عنوان آزمون")
    ExamDate = models.DateField(null=True, blank=True, verbose_name="تاریخ آزمون")
    TotalScore = models.PositiveSmallIntegerField(default=100, verbose_name="نمره کل")

    class Meta:
        managed = True
        db_table = 'lms_web_exam'

    def __str__(self):
        return f"{self.Title} - {self.Course.CourseName}"

class ExamScore(models.Model):
    Exam = models.ForeignKey(Exam, on_delete=models.CASCADE, verbose_name="آزمون")
    Student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="دانشجو")
    Score = models.FloatField(verbose_name="نمره کسب شده")

    class Meta:
        managed = True
        db_table = 'lms_web_examscore'
        unique_together = ('Exam', 'Student')

    def __str__(self):
        return f"{self.Student.PersonID.PersianFirstName} - {self.Exam.Title}"