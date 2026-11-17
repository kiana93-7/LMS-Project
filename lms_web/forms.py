from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Person, Student, Teacher, Course, Education, Certification, CourseCategory


class PersonForm(forms.ModelForm):
    SEX_CHOICES = [('', ' '), ('Male', 'مرد'), ('Female', 'زن')]
    Sex = forms.ChoiceField(label="جنسیت", choices=SEX_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    Birthdate = forms.DateField(label="تاریخ تولد", input_formats=['%Y-%m-%d'], widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))

    class Meta:
        model = Person
        fields = ['PersianFirstName', 'PersianLastName', 'NationalCode', 'Birthdate', 'PhoneNumber', 'Sex']

    def clean_NationalCode(self):
        code = self.cleaned_data.get('NationalCode')
        if code:
            code = str(code).translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789"))
        return code

    def clean_PhoneNumber(self):
        phone = self.cleaned_data.get('PhoneNumber')
        if phone:
            phone = str(phone).translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789"))
        return phone


class StudentForm(forms.ModelForm):
    StudentCode = forms.IntegerField(label="شماره دانشجویی")
    FatherName = forms.CharField(label="نام پدر", max_length=40)
    WorkPhone = forms.CharField(label="شماره تماس پدر", max_length=15, required=False)

    class Meta:
        model = Student
        fields = ['StudentCode', 'FatherName', 'WorkPhone']


class TeacherForm(forms.ModelForm):
    SEX_CHOICES = [('', ' '), ('Male', 'مرد'), ('Female', 'زن')]
    Sex = forms.ChoiceField(label="جنسیت", choices=SEX_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))

    class TeacherForm(forms.ModelForm):
        # ... بقیه فیلدها ...

        # تاریخ تولد میلادی
        Birthdate = forms.DateField(
            label="تاریخ تولد (میلادی)",
            widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        )


    class Meta:
        model = Person
        fields = ['PersianFirstName', 'PersianLastName', 'NationalCode', 'Birthdate', 'PhoneNumber', 'Sex']
        widgets = {
            'Birthdate': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'PersianFirstName': forms.TextInput(attrs={'class': 'form-control'}),
            'PersianLastName': forms.TextInput(attrs={'class': 'form-control'}),
            'NationalCode': forms.TextInput(attrs={'class': 'form-control'}),
            'PhoneNumber': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'PersianFirstName': 'نام (فارسی)',
            'PersianLastName': 'نام خانوادگی (فارسی)',
            'NationalCode': 'کد ملی',
            'Birthdate': 'تاریخ تولد',
            'PhoneNumber': 'شماره تماس',
        }


class CourseForm(forms.ModelForm):
    COURSE_TYPE_CHOICES = [
        ('', ' '),
        ('حضوری', 'حضوری'),
        ('آنلاین', 'آنلاین'),
        ('حضوری و آنلاین', 'حضوری و آنلاین'),
    ]
    CourseType = forms.ChoiceField(label="نوع دوره", choices=COURSE_TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    TeacherID = forms.ModelChoiceField(queryset=Teacher.objects.select_related('PersonID').all(), label="استاد دوره", widget=forms.Select(attrs={'class': 'form-select'}))
    CourseCategoryID = forms.ModelChoiceField(queryset=CourseCategory.objects.all(), label="دسته‌بندی دوره", widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Course
        fields = ['CourseName', 'EnglishCourseName', 'CourseCode', 'Duration', 'CourseType', 'Description', 'CourseCategoryID', 'TeacherID']
        widgets = {
            'Description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'CourseName': forms.TextInput(attrs={'class': 'form-control'}),
            'EnglishCourseName': forms.TextInput(attrs={'class': 'form-control'}),
            'CourseCode': forms.NumberInput(attrs={'class': 'form-control'}),
            'Duration': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'CourseName': 'نام دوره',
            'EnglishCourseName': 'نام دوره (انگلیسی)',
            'CourseCode': 'کد دوره',
            'Duration': 'مدت (ساعت)',
            'Description': 'توضیحات',
        }

class CourseCategoryForm(forms.ModelForm):
    class Meta:
        model = CourseCategory
        fields = ['CourseCategoryName', 'EnglishCourseCategoryName']
        widgets = {
            'CourseCategoryName': forms.TextInput(attrs={'class': 'form-control'}),
            'EnglishCourseCategoryName': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'CourseCategoryName': 'نام دسته‌بندی (فارسی)',
            'EnglishCourseCategoryName': 'نام دسته‌بندی (انگلیسی)',
        }
        
class CombinedEnrollmentForm(forms.Form):
    PersianFirstName = forms.CharField(label="نام (فارسی)", max_length=60, widget=forms.TextInput(attrs={'class': 'form-control'}))
    PersianLastName = forms.CharField(label="نام خانوادگی (فارسی)", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    NationalCode = forms.CharField(label="کد ملی", max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    PhoneNumber = forms.CharField(label="شماره تماس", max_length=11, widget=forms.TextInput(attrs={'class': 'form-control'}))
    Birthdate = forms.DateField(label="تاریخ تولد", widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    Sex = forms.ChoiceField(label="جنسیت", choices=[('', ' '), ('Male', 'مرد'), ('Female', 'زن')], widget=forms.Select(attrs={'class': 'form-select'}))
    StudentCode = forms.IntegerField(label="شماره دانشجویی", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    FatherName = forms.CharField(label="نام پدر", max_length=40, widget=forms.TextInput(attrs={'class': 'form-control'}))
    CourseID = forms.ModelChoiceField(queryset=Course.objects.all(), label="دوره مورد نظر", widget=forms.Select(attrs={'class': 'form-select'}))


class AdminStudentRegistrationForm(forms.Form):
    PersianFirstName = forms.CharField(label="نام (فارسی)", max_length=60,
                                       widget=forms.TextInput(attrs={'class': 'form-control'}))
    PersianLastName = forms.CharField(label="نام خانوادگی (فارسی)", max_length=100,
                                      widget=forms.TextInput(attrs={'class': 'form-control'}))
    NationalCode = forms.CharField(label="کد ملی", max_length=20,
                                   widget=forms.TextInput(attrs={'class': 'form-control'}))
    PhoneNumber = forms.CharField(label="شماره تماس", max_length=11,
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))

    Birthdate = forms.DateField(
        label="تاریخ تولد (میلادی)",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    Sex = forms.ChoiceField(label="جنسیت", choices=[('', ' '), ('Male', 'مرد'), ('Female', 'زن')],
                            widget=forms.Select(attrs={'class': 'form-select'}))
    StudentCode = forms.IntegerField(label="شماره دانشجویی", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    FatherName = forms.CharField(label="نام پدر", max_length=40,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    CourseID = forms.ModelChoiceField(queryset=Course.objects.all(), label="دوره مورد نظر",
                                      widget=forms.Select(attrs={'class': 'form-select'}))

class GradeForm(forms.Form):
    StudentID = forms.ModelChoiceField(
        queryset=Student.objects.select_related('PersonID').all(),
        label="دانشجو",
        empty_label="",  # <--- این خط رو حتماً اضافه کن (یا خالی بذار)
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_student_select'})
    )
    CourseName = forms.CharField(label="دوره", required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': True, 'id': 'id_course_display'}))
    TermNumber = forms.CharField(label="شماره ترم", required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': True, 'id': 'id_term_display'}))
    Score = forms.IntegerField(label="نمره", min_value=0, max_value=100, widget=forms.NumberInput(attrs={'class': 'form-control'}))

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class CustomLoginForm(AuthenticationForm):
    pass


class CertificationForm(forms.ModelForm):
    CertificationTitle = forms.ChoiceField(
        label="عنوان مدرک (دوره)",
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # تاریخ صدور (میلادی)
    Startdate = forms.DateField(
        label="تاریخ صدور (میلادی)",
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )

    class Meta:
        model = Certification
        fields = ['CertificationTitle', 'Vendor', 'Startdate']
        widgets = {
            'Vendor': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'Vendor': 'صادرکننده',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        courses = Course.objects.all()
        self.fields['CertificationTitle'].choices = [('', ' ')] + [(c.CourseName, c.CourseName) for c in courses]