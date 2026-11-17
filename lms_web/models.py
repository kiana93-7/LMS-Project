from django.db import models


# ==================== Education ====================
class Education(models.Model):
    ID = models.AutoField(primary_key=True, db_column='ID')
    EducationName = models.CharField(max_length=40, db_column='EducationName', verbose_name="نام مدرک")

    class Meta:
        managed = False
        db_table = 'Education'
        ordering = ['ID']
        verbose_name = "مدرک تحصیلی"
        verbose_name_plural = "مدارک تحصیلی"

    def __str__(self):
        return self.EducationName


# ==================== Person ====================
class Person(models.Model):
    ID = models.AutoField(primary_key=True, db_column='ID')
    PersianFirstName = models.CharField(max_length=60, db_column='PersianFirstName', verbose_name="نام (فارسی)")
    EnglishFirstName = models.CharField(max_length=20, null=True, blank=True, db_column='EnglishFirstName', verbose_name="نام (انگلیسی)")
    PersianLastName = models.CharField(max_length=100, db_column='PersianLastName', verbose_name="نام خانوادگی (فارسی)")
    EnglishLastName = models.CharField(max_length=30, null=True, blank=True, db_column='EnglishLastName', verbose_name="نام خانوادگی (انگلیسی)")
    NationalCode = models.CharField(max_length=20, unique=True, db_column='NationalCode', verbose_name="کد ملی")
    Sex = models.CharField(max_length=20, db_column='Sex', verbose_name="جنسیت")
    Birthdate = models.DateField(db_column='Birthdate', verbose_name="تاریخ تولد")
    HomeAddress = models.CharField(max_length=400, null=True, blank=True, db_column='HomeAddress', verbose_name="آدرس منزل")
    PhoneNumber = models.CharField(max_length=11, db_column='PhoneNumber', verbose_name="شماره تماس")
    EmailAddress = models.CharField(max_length=100, null=True, blank=True, db_column='EmailAddress', verbose_name="ایمیل")
    EducationID = models.ForeignKey(Education, on_delete=models.DO_NOTHING, db_column='EducationID', verbose_name="مدرک تحصیلی")

    class Meta:
        managed = False
        db_table = 'Person'
        ordering = ['ID']
        verbose_name = "شخص"
        verbose_name_plural = "اشخاص"

    def __str__(self):
        return f"{self.PersianFirstName} {self.PersianLastName}"


# ==================== Student ====================
class Student(models.Model):
    PersonID = models.OneToOneField(Person, on_delete=models.DO_NOTHING, primary_key=True, db_column='PersonID', verbose_name="شخص")
    StudentCode = models.IntegerField(db_column='StudentCode', verbose_name="شماره دانشجویی")
    FatherName = models.CharField(max_length=40, db_column='FatherName', verbose_name="نام پدر")
    WorkAddress = models.CharField(max_length=400, null=True, blank=True, db_column='WorkAddress', verbose_name="آدرس محل کار")
    WorkPhone = models.CharField(max_length=15, null=True, blank=True, db_column='WorkPhone', verbose_name="تلفن محل کار")

    class Meta:
        managed = False
        db_table = 'Student'
        ordering = ['PersonID']
        verbose_name = "دانشجو"
        verbose_name_plural = "دانشجویان"

    def __str__(self):
        return f"{self.PersonID.PersianFirstName} {self.PersonID.PersianLastName} - {self.StudentCode}"


# ==================== Teacher ====================
class Teacher(models.Model):
    PersonID = models.OneToOneField(Person, on_delete=models.DO_NOTHING, primary_key=True, db_column='PersonID', verbose_name="شخص")
    TeacherCode = models.IntegerField(db_column='TeacherCode', verbose_name="کد استاد")
    MaritalStatus = models.CharField(max_length=40, db_column='MaritalStatus', verbose_name="وضعیت تاهل")
    Startdate = models.DateField(db_column='Startdate', verbose_name="تاریخ شروع همکاری")
    InsuranceNumber = models.CharField(max_length=10, null=True, blank=True, db_column='InsuranceNumber', verbose_name="شماره بیمه")
    AccountNumber = models.CharField(max_length=16, null=True, blank=True, db_column='AccountNumber', verbose_name="شماره حساب")

    class Meta:
        managed = False
        db_table = 'Teacher'
        ordering = ['PersonID']
        verbose_name = "استاد"
        verbose_name_plural = "اساتید"

    def __str__(self):
        return f"{self.PersonID.PersianFirstName} {self.PersonID.PersianLastName}"


# ==================== CourseCategory ====================
class CourseCategory(models.Model):
    ID = models.AutoField(primary_key=True, db_column='ID')
    CourseCategoryName = models.CharField(max_length=100, db_column='CourseCategoryName', verbose_name="نام دسته‌بندی")
    EnglishCourseCategoryName = models.CharField(max_length=50, db_column='EnglishCourseCategoryName', verbose_name="نام دسته‌بندی (انگلیسی)")

    class Meta:
        managed = False
        db_table = 'CourseCategory'
        ordering = ['ID']
        verbose_name = "دسته‌بندی دوره"
        verbose_name_plural = "دسته‌بندی‌های دوره"

    def __str__(self):
        return self.CourseCategoryName


# ==================== Course ====================
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
    TeacherID = models.ForeignKey(Teacher, on_delete=models.DO_NOTHING, null=True, blank=True, db_column='TeacherID',verbose_name="استاد")
    class Meta:
        managed = False
        db_table = 'Course'
        ordering = ['ID']
        verbose_name = "دوره"
        verbose_name_plural = "دوره‌ها"

    def __str__(self):
        return self.CourseName


# ==================== StudentCourseTeacher ====================
class StudentCourseTeacher(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')  # ← id واقعی
    StudentID = models.ForeignKey(Student, on_delete=models.DO_NOTHING, db_column='StudentID', verbose_name="دانشجو")
    CourseID = models.ForeignKey(Course, on_delete=models.DO_NOTHING, db_column='CourseID', verbose_name="دوره")
    TeacherID = models.ForeignKey(Teacher, on_delete=models.DO_NOTHING, db_column='TeacherID', verbose_name="استاد")
    TermNumber = models.IntegerField(db_column='TermNumber', verbose_name="شماره ترم")
    Score = models.SmallIntegerField(db_column='Score', verbose_name="نمره")

    class Meta:
        managed = False
        db_table = 'Student_Course_Teacher'
        ordering = ['id']
        verbose_name = "ثبت‌نام"
        verbose_name_plural = "ثبت‌نام‌ها"

    def __str__(self):
        return f"{self.StudentID.PersonID.PersianFirstName} - {self.CourseID.CourseName}"


# ==================== Certification ====================
class Certification(models.Model):
    ID = models.AutoField(primary_key=True, db_column='ID')
    CertificationTitle = models.CharField(max_length=70, db_column='CertificationTitle', verbose_name="عنوان مدرک")
    Vendor = models.CharField(max_length=50, db_column='Vendor', verbose_name="صادرکننده")
    Startdate = models.DateField(db_column='Startdate', verbose_name="تاریخ صدور")

    class Meta:
        managed = False
        db_table = 'Certification'
        ordering = ['ID']
        verbose_name = "مدرک"
        verbose_name_plural = "مدارک"

    def __str__(self):
        return self.CertificationTitle


# ==================== TeacherCertification ====================
class TeacherCertification(models.Model):
    TeacherID = models.ForeignKey(Teacher, on_delete=models.DO_NOTHING, db_column='TeacherID', verbose_name="استاد")
    CertificationID = models.ForeignKey(Certification, on_delete=models.DO_NOTHING, db_column='CertificationID', verbose_name="مدرک")
    Score = models.SmallIntegerField(db_column='Score', verbose_name="نمره")
    Expiredate = models.DateField(null=True, blank=True, db_column='Expiredate', verbose_name="تاریخ انقضا")

    class Meta:
        managed = False
        db_table = 'Teacher_Certification'
        ordering = ['TeacherID', 'CertificationID']
        verbose_name = "مدرک استاد"
        verbose_name_plural = "مدارک اساتید"

    def __str__(self):
        return f"{self.TeacherID.PersonID.PersianFirstName} - {self.CertificationID.CertificationTitle}"


class Exam(models.Model):
    # ✅ اینجا صریحاً نوع رو smallint تعیین می‌کنیم تا با Course.ID هماهنگ باشه
    Course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        db_column='Course_id',
        to_field='ID', # اشاره به همون فیلد ID
        verbose_name="دوره"
    )
    Title = models.CharField(max_length=100, verbose_name="عنوان آزمون")
    ExamDate = models.DateField(null=True, blank=True, verbose_name="تاریخ آزمون")
    TotalScore = models.PositiveSmallIntegerField(default=100, verbose_name="نمره کل")

    class Meta:
        db_table = 'lms_web_exam'

    def __str__(self):
        return f"{self.Title} - {self.Course.CourseName}"

class ExamScore(models.Model):
    # نمره هر دانشجو در یک آزمون خاص
    Exam = models.ForeignKey(Exam, on_delete=models.CASCADE, verbose_name="آزمون")
    Student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="دانشجو")
    Score = models.FloatField(verbose_name="نمره کسب شده")

    class Meta:
        unique_together = ('Exam', 'Student') # هر دانشجو در هر آزمون فقط یک نمره

    def __str__(self):
        return f"{self.Student.PersonID.PersianFirstName} - {self.Exam.Title}"