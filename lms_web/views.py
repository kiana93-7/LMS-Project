from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from datetime import date
from .models import Course, Teacher, Person, Student, StudentCourseTeacher, Certification, Education, CourseCategory, \
    TeacherCertification, ExamScore, Exam
from .forms import PersonForm, StudentForm, CourseForm, TeacherForm, GradeForm, CustomUserCreationForm, CombinedEnrollmentForm, AdminStudentRegistrationForm, CertificationForm, CourseCategoryForm
from django.http import HttpResponse
import jdatetime
from django.core.mail import send_mail
from django.conf import settings


def get_default_education():
    return Education.objects.filter(pk=2).first() or Education.objects.first()


def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'lms_web/signup.html', {'form': form})


def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next')
    if next_url in (None, '', 'None', 'none'):
        next_url = None

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'lms_web/login.html', {'form': form, 'next': next_url})


@require_POST
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='/login/')
def home_view(request):
    latest_courses = Course.objects.all().order_by('-ID')[:3]
    context = {
        'latest_courses': latest_courses,
        'course_count': Course.objects.count(),
        'teacher_count': Teacher.objects.count(),
        'student_count': Student.objects.exclude(PersonID__NationalCode='0000000000').count(),
        'cert_count': Certification.objects.count(),
    }
    return render(request, 'lms_web/home.html', context)


@login_required(login_url='/login/')
def course_list_view(request):
    # استاد رو از خود جدول Course می‌خونیم (select_related برای بهینه‌سازی)
    courses = Course.objects.all().select_related('TeacherID__PersonID')

    course_type = request.GET.get('course_type')
    if course_type:
        courses = courses.filter(CourseType=course_type)

    raw_types = Course.objects.values_list('CourseType', flat=True).distinct()
    course_types = list(set([t.strip() for t in raw_types if t and t.strip()]))

    paginator = Paginator(courses, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for course in page_obj:
        # استاد مستقیماً از خود دوره خونده می‌شه
        if course.TeacherID:
            t = course.TeacherID.PersonID
            course.teacher_name = f"{t.PersianFirstName} {t.PersianLastName}"
        else:
            course.teacher_name = "تعیین نشده"

    return render(request, 'lms_web/course_list.html', {
        'courses': page_obj,
        'course_types': course_types,
        'page_obj': page_obj
    })

@login_required(login_url='/login/')
def course_create_view(request):
    if not request.user.is_superuser:
        return render(request, 'lms_web/403.html', status=403)
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.Syllabus = "سرفصل‌ها متعاقباً اعلام می‌شود."
            course.save()  # استاد (TeacherID) هم خودکار توی همین مرحله ذخیره می‌شه

            messages.success(request, 'دوره با موفقیت ایجاد شد.')
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'lms_web/course_create.html', {'form': form})


@login_required(login_url='/login/')
def course_update_view(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            # ⚠️ اینجا استاد رو از فرم بگیر و توی خود دوره ذخیره کن
            course = form.save(commit=False)
            course.TeacherID = form.cleaned_data['TeacherID']
            course.save()

            messages.success(request, 'دوره با موفقیت ویرایش شد!')
            return redirect(f"/courses/?page={request.GET.get('page', 1)}")
    else:
        form = CourseForm(instance=course)

    return render(request, 'lms_web/course_create.html', {'form': form})

@login_required(login_url='/login/')
def course_delete_view(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        StudentCourseTeacher.objects.filter(CourseID=course).delete()
        course.delete()
        return redirect('course_list')
    return render(request, 'lms_web/course_delete.html', {'course': course})


@login_required(login_url='/login/')
def course_detail_view(request, pk):
    course = get_object_or_404(Course, pk=pk)
    e = StudentCourseTeacher.objects.filter(CourseID=course).select_related('TeacherID__PersonID').first()
    return render(request, 'lms_web/course_detail.html', {
        'course': course,
        'teacher': course.TeacherID
    })


@login_required(login_url='/login/')
def teacher_list_view(request):
    # گرفتن همه اساتید
    teachers = Teacher.objects.select_related('PersonID').all()

    for teacher in teachers:
        # پیدا کردن دوره‌هایی که مستقیماً به این استاد تخصیص داده شدن
        teacher.courses_list = Course.objects.filter(TeacherID=teacher)

    return render(request, 'lms_web/teacher_list.html', {'teachers': teachers})

@login_required(login_url='/login/')
def teacher_create_view(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            try:
                person = form.save(commit=False)
                person.EnglishFirstName = "-"
                person.EnglishLastName = "-"
                person.EducationID = get_default_education()
                person.save()

                last = Teacher.objects.order_by('-TeacherCode').first()
                next_code = (last.TeacherCode + 1) if last else 1001
                Teacher.objects.create(
                    PersonID=person,
                    TeacherCode=next_code,
                    MaritalStatus="Single",
                    Startdate=date.today(),
                    InsuranceNumber="1234567890",
                    AccountNumber="1234567890123456",
                )
                messages.success(request, 'استاد با موفقیت ثبت شد!')
                return redirect('teacher_list')
            except Exception as e:
                messages.error(request, f'خطا در ثبت اطلاعات: {e}')
    else:
        form = TeacherForm()

    return render(request, 'lms_web/teacher_create.html', {'person_form': form})

@login_required(login_url='/login/')
def teacher_delete_view(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        StudentCourseTeacher.objects.filter(TeacherID=teacher.pk).delete()
        TeacherCertification.objects.filter(TeacherID=teacher.pk).delete()
        person = teacher.PersonID
        teacher.delete()
        person.delete()
        return redirect('teacher_list')
    return render(request, 'lms_web/teacher_delete.html', {'teacher': teacher})


@login_required(login_url='/login/')
def teacher_update_view(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    person = teacher.PersonID
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=person)
        if form.is_valid():
            form.save()
            messages.success(request, 'اطلاعات استاد با موفقیت ویرایش شد!')
            return redirect('teacher_list')
    else:
        # پر کردن فرم با تاریخ فعلی
        birthdate_str = person.Birthdate.strftime('%Y-%m-%d') if person.Birthdate else ''
        form = TeacherForm(instance=person, initial={'Birthdate': birthdate_str})
    return render(request, 'lms_web/teacher_create.html', {'person_form': form})

@login_required(login_url='/login/')
def teacher_detail_view(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    teacher_courses = StudentCourseTeacher.objects.filter(TeacherID=teacher.pk).values_list('CourseID', flat=True).distinct()
    courses = Course.objects.filter(pk__in=teacher_courses)
    return render(request, 'lms_web/teacher_detail.html', {'teacher': teacher, 'courses': courses})


@login_required(login_url='/login/')
def student_register_view(request):
    if not request.user.is_staff:
        return render(request, 'lms_web/403.html', status=403)

    if request.method == 'POST':
        form = AdminStudentRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # ۱. ذخیره اطلاعات شخص
                person = Person(
                    PersianFirstName=form.cleaned_data['PersianFirstName'],
                    PersianLastName=form.cleaned_data['PersianLastName'],
                    NationalCode=form.cleaned_data['NationalCode'],
                    PhoneNumber=form.cleaned_data['PhoneNumber'],
                    Birthdate=form.cleaned_data['Birthdate'],
                    Sex=form.cleaned_data['Sex'],
                    EnglishFirstName="-", EnglishLastName="-",
                    EducationID=get_default_education(),
                )
                person.save()

                # ۲. ذخیره اطلاعات دانشجو
                student = Student(
                    PersonID=person,
                    StudentCode=form.cleaned_data['StudentCode'],
                    FatherName=form.cleaned_data['FatherName']
                )
                student.save()

                # ۳. پیدا کردن استاد دوره به صورت خودکار
                course = form.cleaned_data['CourseID']
                teacher = course.TeacherID
                if not teacher:
                    teacher = Teacher.objects.first()

                # ۴. ثبت‌نام در دوره
                StudentCourseTeacher.objects.create(
                    StudentID=student,
                    CourseID=course,
                    TeacherID=teacher,
                    TermNumber=1,
                    Score=0,
                )

                # ۵. ارسال ایمیل
                try:
                    subject = '🎓 خوش آمدید به سیستم مدیریت آموزش'
                    message = f"سلام {person.PersianFirstName} عزیز،\n\n"
                    message += f"ثبت‌نام شما در دوره «{course.CourseName}» با موفقیت انجام شد.\n"
                    message += f"شماره دانشجویی شما: {student.StudentCode}\n\n"
                    message += "به خانواده بزرگ ما خوش آمدید! 🚀"

                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, ['student@example.com'], fail_silently=False)
                except Exception as email_error:
                    print(f"❌ خطا در ارسال ایمیل: {email_error}")

                messages.success(request, 'دانشجو با موفقیت ثبت‌نام شد!')
                # ✅ تغییر مهم: ریدایرکت به لیست ثبت‌نام‌ها
                return redirect('enrollment_list')

            except Exception as e:
                messages.error(request, f'خطا در ثبت اطلاعات: {e}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'فیلد «{field}»: {error}')
    else:
        form = AdminStudentRegistrationForm()

    return render(request, 'lms_web/student_register.html', {'form': form})

@login_required(login_url='/login/')
def student_list_view(request):
    if not request.user.is_superuser:
        return render(request, 'lms_web/403.html', status=403)
    students = Student.objects.exclude(PersonID__NationalCode='0000000000').select_related('PersonID')
    return render(request, 'lms_web/student_list.html', {'students': students})


@login_required(login_url='/login/')
def student_delete_view(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        StudentCourseTeacher.objects.filter(StudentID=student).delete()
        person = student.PersonID
        student.delete()
        person.delete()
        messages.success(request, 'دانشجو با موفقیت حذف شد!')
        return redirect('student_list')
    return render(request, 'lms_web/student_delete.html', {'student': student})

@login_required(login_url='/login/')
def student_update_view(request, pk):
    student = get_object_or_404(Student, pk=pk)
    person = student.PersonID
    if request.method == 'POST':
        form = AdminStudentRegistrationForm(request.POST)
        if form.is_valid():
            person.PersianFirstName = form.cleaned_data['PersianFirstName']
            person.PersianLastName = form.cleaned_data['PersianLastName']
            person.NationalCode = form.cleaned_data['NationalCode']
            person.PhoneNumber = form.cleaned_data['PhoneNumber']
            person.Birthdate = form.cleaned_data['Birthdate']
            person.Sex = form.cleaned_data['Sex']
            person.save()
            student.StudentCode = form.cleaned_data['StudentCode']
            student.FatherName = form.cleaned_data['FatherName']
            student.save()
            course = form.cleaned_data['CourseID']
            enrollment = StudentCourseTeacher.objects.filter(StudentID=student).first()
            if enrollment:
                enrollment.CourseID = course
                enrollment.save()
            else:
                StudentCourseTeacher.objects.create(
                    StudentID=student, CourseID=course,
                    TeacherID=Teacher.objects.first(), TermNumber=1, Score=0,
                )
            return redirect('student_list')
    else:
        birthdate_str = person.Birthdate.strftime('%Y-%m-%d') if person.Birthdate else ''
        enrollment = StudentCourseTeacher.objects.filter(StudentID=student).first()
        initial_data = {
            'PersianFirstName': person.PersianFirstName,
            'PersianLastName': person.PersianLastName,
            'NationalCode': person.NationalCode,
            'PhoneNumber': person.PhoneNumber,
            'Birthdate': birthdate_str,
            'Sex': person.Sex,
            'StudentCode': student.StudentCode,
            'FatherName': student.FatherName,
        }
        if enrollment and enrollment.CourseID:
            initial_data['CourseID'] = enrollment.CourseID.pk
        form = AdminStudentRegistrationForm(initial=initial_data)
    return render(request, 'lms_web/student_register.html', {'form': form})


@login_required(login_url='/login/')
def enrollment_view(request):
    if request.method == 'POST':
        form = CombinedEnrollmentForm(request.POST)
        if form.is_valid():
            person = Person(
                PersianFirstName=form.cleaned_data['PersianFirstName'],
                PersianLastName=form.cleaned_data['PersianLastName'],
                NationalCode=form.cleaned_data['NationalCode'],
                PhoneNumber=form.cleaned_data['PhoneNumber'],
                Birthdate=form.cleaned_data['Birthdate'],
                Sex=form.cleaned_data['Sex'],
                EnglishFirstName="-", EnglishLastName="-",
                EducationID=get_default_education(),
            )
            person.save()

            student = Student(
                PersonID=person,
                StudentCode=form.cleaned_data['StudentCode'],
                FatherName=form.cleaned_data['FatherName']
            )
            student.save()

            # ✅ تغییر اصلی اینجاست
            course = form.cleaned_data['CourseID']
            teacher = course.TeacherID  # استادِ مربوط به همین دوره رو برمی‌داریم

            StudentCourseTeacher.objects.create(
                StudentID=student,
                CourseID=course,
                TeacherID=teacher,
                TermNumber=1,
                Score=0,
            )
            messages.success(request, 'ثبت‌نام شما با موفقیت انجام شد!')
            return redirect('course_list')
    else:
        course_id = request.GET.get('course_id')
        form = CombinedEnrollmentForm(initial={'CourseID': course_id} if course_id else {})
    return render(request, 'lms_web/enrollment.html', {'form': form})

@login_required(login_url='/login/')
def enrollment_list_view(request):
    if not request.user.is_superuser:
        return render(request, 'lms_web/403.html', status=403)
    enrollments = StudentCourseTeacher.objects.select_related('StudentID__PersonID', 'CourseID', 'TeacherID__PersonID').all()
    return render(request, 'lms_web/enrollment_list.html', {'enrollments': enrollments})

@login_required(login_url='/login/')
def enrollment_delete_view(request, pk):
    enrollment = get_object_or_404(StudentCourseTeacher, pk=pk)
    if request.method == 'POST':
        enrollment.delete()
        return redirect('enrollment_list')
    return render(request, 'lms_web/enrollment_delete.html', {'enrollment': enrollment})

@login_required(login_url='/login/')
def register_grade_view(request):
    if not request.user.is_superuser:
        return render(request, 'lms_web/403.html', status=403)
    if request.method == 'POST':
        form = GradeForm(request.POST)
        if form.is_valid():
            student = form.cleaned_data['StudentID']
            score = form.cleaned_data['Score']
            enrollment_id = request.POST.get('enrollment_id')
            enrollment = StudentCourseTeacher.objects.filter(pk=enrollment_id).first() if enrollment_id else StudentCourseTeacher.objects.filter(StudentID=student).first()
            if enrollment:
                enrollment.Score = score
                enrollment.save()
                messages.success(request, 'نمره با موفقیت ثبت شد!')
                return redirect('register_grade')
            form.add_error(None, 'این دانشجو در هیچ دوره‌ای ثبت‌نام نکرده است.')
    else:
        form = GradeForm()
    return render(request, 'lms_web/register_grade.html', {'form': form})


@login_required(login_url='/login/')
def get_student_course_info(request, student_id):
    try:
        # لاگ کردن برای دیباگ
        print(f"DEBUG: Searching for student_id = {student_id}")

        # جستجوی رکورد ثبت‌نام
        e = StudentCourseTeacher.objects.filter(StudentID=student_id).select_related('CourseID').first()

        if e:
            print(f"DEBUG: Found enrollment - Course: {e.CourseID.CourseName}, Term: {e.TermNumber}, ID: {e.id}")
            return JsonResponse({
                'course_name': e.CourseID.CourseName,
                'term_number': e.TermNumber,
                'enrollment_id': e.id
            })

        print(f"DEBUG: No enrollment found for student_id = {student_id}")
        return JsonResponse({'error': 'این دانشجو در هیچ دوره‌ای ثبت‌نام نکرده است.'})

    except Exception as ex:
        print(f"DEBUG ERROR: {str(ex)}")
        return JsonResponse({'error': f'خطای سیستم: {str(ex)}'})


@login_required(login_url='/login/')
def certificate_create_view(request):
    if not request.user.is_superuser:
        return render(request, 'lms_web/403.html', status=403)

    if request.method == 'POST':
        form = CertificationForm(request.POST)
        if form.is_valid():
            try:
                cert = form.save(commit=False)
                cert.Startdate = form.cleaned_data['Startdate']  # تاریخ مستقیم میلادی ذخیره می‌شه
                cert.save()

                messages.success(request, 'مدرک با موفقیت ثبت شد!')
                return redirect('certificate_create')
            except Exception as e:
                messages.error(request, f'خطا در ثبت اطلاعات: {e}')
    else:
        form = CertificationForm()

    return render(request, 'lms_web/certificate_create.html', {'form': form})

@login_required(login_url='/login/')
def course_calendar_view(request):
    enrollments = StudentCourseTeacher.objects.select_related('CourseID').all()
    terms = {}
    for e in enrollments:
        terms.setdefault(e.TermNumber, [])
        if e.CourseID not in terms[e.TermNumber]:
            terms[e.TermNumber].append(e.CourseID)
    return render(request, 'lms_web/course_calendar.html', {'terms': terms})

@login_required(login_url='/login/')
def category_list_view(request):
    if not request.user.is_superuser:
        return render(request, 'lms_web/403.html', status=403)
    categories = CourseCategory.objects.all()
    return render(request, 'lms_web/category_list.html', {'categories': categories})

@login_required(login_url='/login/')
def category_create_view(request):
    if not request.user.is_superuser:
        return render(request, 'lms_web/403.html', status=403)
    if request.method == 'POST':
        form = CourseCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'دسته‌بندی با موفقیت اضافه شد!')
            return redirect('category_list')
    else:
        form = CourseCategoryForm()
    return render(request, 'lms_web/category_create.html', {'form': form})

@login_required(login_url='/login/')
def category_update_view(request, pk):
    if not request.user.is_superuser:
        return render(request, 'lms_web/403.html', status=403)
    category = get_object_or_404(CourseCategory, pk=pk)
    if request.method == 'POST':
        form = CourseCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'دسته‌بندی ویرایش شد!')
            return redirect('category_list')
    else:
        form = CourseCategoryForm(instance=category)
    return render(request, 'lms_web/category_create.html', {'form': form})

@login_required(login_url='/login/')
def category_delete_view(request, pk):
    if not request.user.is_superuser:
        return render(request, 'lms_web/403.html', status=403)
    category = get_object_or_404(CourseCategory, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'دسته‌بندی حذف شد!')
        return redirect('category_list')
    return render(request, 'lms_web/category_delete.html', {'category': category})


@login_required(login_url='/login/')
def exam_list_view(request):
    if not request.user.is_superuser:
        return render(request, 'lms_web/403.html', status=403)

    course_ids = StudentCourseTeacher.objects.values_list('CourseID', flat=True).distinct()
    courses = Course.objects.filter(ID__in=course_ids)

    return render(request, 'lms_web/exam_list.html', {'courses': courses})


@login_required(login_url='/login/')
def exam_detail_view(request, course_id):
    if not request.user.is_superuser:
        return render(request, 'lms_web/403.html', status=403)

    course = get_object_or_404(Course, pk=course_id)
    enrollments = StudentCourseTeacher.objects.filter(CourseID=course).select_related('StudentID__PersonID')

    if request.method == 'POST':
        enrollment_id = request.POST.get('enrollment_id')
        score = request.POST.get('score')
        enrollment = get_object_or_404(StudentCourseTeacher, pk=enrollment_id)
        enrollment.Score = score
        enrollment.save()
        messages.success(request, 'نمره آزمون با موفقیت ثبت شد!')
        return redirect('exam_detail', course_id=course_id)

    return render(request, 'lms_web/exam_detail.html', {
        'course': course,
        'enrollments': enrollments
    })


@login_required(login_url='/login/')
def certificate_list_view(request):
    if not request.user.is_superuser:
        return render(request, 'lms_web/403.html', status=403)

    # گرفتن همه مدارک از دیتابیس
    certificates = Certification.objects.all().order_by('-Startdate')

    return render(request, 'lms_web/certificate_list.html', {'certificates': certificates})


from django.views.decorators.http import require_POST


@login_required(login_url='/login/')
@require_POST
def delete_all_students_view(request):
    if not request.user.is_superuser:
        return render(request, 'lms_web/403.html', status=403)

    try:
        # ۱. پاک کردن همه ثبت‌نام‌ها
        StudentCourseTeacher.objects.all().delete()

        # ۲. پاک کردن همه دانشجوها
        Student.objects.all().delete()

        # ۳. پاک کردن اطلاعات شخصی (Person) مربوط به دانشجوها
        # چون ممکنه Personهای دیگه‌ای (مثل استاد) هم وجود داشته باشن،
        # فقط Personهایی رو پاک میکنیم که دانشجوی خاصی بهشون وصل نیست
        # ولی برای سادگی در تست، اینجا همه Personهایی که استاد نیستن رو پاک میکنیم
        Person.objects.filter(student__isnull=True, teacher__isnull=True).delete()

        messages.success(request, 'تمام دانشجوها و ثبت‌نام‌ها با موفقیت پاک شدند!')
    except Exception as e:
        messages.error(request, f'خطا در پاک‌سازی: {e}')

    return redirect('student_list')


# ==========================================
# بخش مدیریت آزمون‌ها (Exams)
# ==========================================

@login_required(login_url='/login/')
def exam_list_view(request):
    if not request.user.is_superuser:
        return render(request, 'lms_web/403.html', status=403)

    # گرفتن دوره‌هایی که حداقل یک دانشجو ثبت‌نام شده دارند
    course_ids = StudentCourseTeacher.objects.values_list('CourseID', flat=True).distinct()
    courses = Course.objects.filter(ID__in=course_ids)

    return render(request, 'lms_web/exam_list.html', {'courses': courses})


@login_required(login_url='/login/')
def exam_detail_view(request, course_id):
    if not request.user.is_superuser:
        return render(request, 'lms_web/403.html', status=403)

    course = get_object_or_404(Course, pk=course_id)
    exams = Exam.objects.filter(Course=course).order_by('-id')

    # اگر فرم ساخت آزمون جدید ارسال شده بود
    if request.method == 'POST' and 'create_exam' in request.POST:
        title = request.POST.get('title')
        total_score = request.POST.get('total_score', 100)

        if title:
            Exam.objects.create(
                Course=course,
                Title=title,
                TotalScore=total_score
            )
            messages.success(request, 'آزمون جدید با موفقیت ساخته شد!')
            return redirect('exam_detail', course_id=course_id)
        else:
            messages.error(request, 'عنوان آزمون نمی‌تواند خالی باشد.')

    return render(request, 'lms_web/exam_detail.html', {
        'course': course,
        'exams': exams
    })


@login_required(login_url='/login/')
def exam_grade_view(request, exam_id):
    if not request.user.is_staff:  # یا is_superuser
        return render(request, 'lms_web/403.html', status=403)

    exam = get_object_or_404(Exam, pk=exam_id)
    enrollments = StudentCourseTeacher.objects.filter(CourseID=exam.Course).select_related('StudentID__PersonID')

    if request.method == 'POST':
        for enrollment in enrollments:
            student_id = enrollment.StudentID.pk
            score_val = request.POST.get(f'score_{student_id}')

            # ۱. اول چک می‌کنیم که آیا استاد اصلاً چیزی توی فیلد نمره نوشته یا نه
            if score_val is not None and str(score_val).strip() != '':
                try:
                    numeric_score = float(score_val)

                    # ۲. سعی می‌کنیم رکورد موجود رو پیدا کنیم
                    score_obj = ExamScore.objects.filter(Exam=exam, Student=enrollment.StudentID).first()

                    if score_obj:
                        # اگه رکورد بود، فقط مقدارش رو آپدیت می‌کنیم
                        score_obj.Score = numeric_score
                        score_obj.save()
                    else:
                        # اگه نبود، رکورد جدید WITH SCORE (نه با None) می‌سازیم
                        ExamScore.objects.create(
                            Exam=exam,
                            Student=enrollment.StudentID,
                            Score=numeric_score  # مقدار معتبر
                        )
                except ValueError:
                    messages.error(request,
                                   f'مقدار وارد شده برای دانشجو {enrollment.StudentID.PersonID.PersianFirstName} عدد نیست.')
                    return redirect('exam_grade', exam_id=exam_id)
            else:
                # ۳. اگر فیلد خالی بود، اصلاً رکوردی ساخته نمی‌شه و اگر بود پاک می‌شه
                ExamScore.objects.filter(Exam=exam, Student=enrollment.StudentID).delete()

        messages.success(request, 'نمرات با موفقیت ذخیره شد!')
        return redirect('exam_grade', exam_id=exam_id)

    # آماده‌سازی لیست برای نمایش در فرم
    students_data = []
    for enrollment in enrollments:
        existing_score = ExamScore.objects.filter(Exam=exam, Student=enrollment.StudentID).first()
        students_data.append({
            'student': enrollment.StudentID,
            'current_score': existing_score.Score if existing_score else ''
        })

    return render(request, 'lms_web/exam_grade.html', {
        'exam': exam,
        'students_data': students_data
    })

@login_required(login_url='/login/')
def student_exams_view(request):
    # ۱. پیدا کردن دانشجو بر اساس شماره تلفن یا ایمیل کاربری که لاگین کرده
    student = None

    # تلاش با شماره تلفن
    if request.user.username:
        student = Student.objects.filter(PersonID__PhoneNumber=request.user.username).select_related('PersonID').first()

    # تلاش با ایمیل (اگر با شماره تلفن پیدا نشد)
    if not student and request.user.email:
        student = Student.objects.filter(PersonID__EmailAddress=request.user.email).select_related('PersonID').first()

    # اگر دانشجو پیدا نشد (مثلاً ادمین وارد شده)
    if not student:
        messages.warning(request, 'اطلاعات دانشجویی برای این حساب کاربری یافت نشد. لطفاً با پشتیبانی تماس بگیرید.')
        return redirect('home')

    # ۲. گرفتن دوره‌هایی که این دانشجو ثبت‌نام کرده
    enrollments = StudentCourseTeacher.objects.filter(StudentID=student).select_related('CourseID',
                                                                                        'TeacherID__PersonID')

    courses_data = []
    for enrollment in enrollments:
        course = enrollment.CourseID

        # گرفتن آزمون‌های این دوره
        exams = Exam.objects.filter(Course=course)

        exam_list = []
        for exam in exams:
            # گرفتن نمره این دانشجو در این آزمون
            score_obj = ExamScore.objects.filter(Exam=exam, Student=student).first()
            exam_list.append({
                'title': exam.Title,
                'total_score': exam.TotalScore,
                'score': score_obj.Score if score_obj else None
            })

        courses_data.append({
            'course_name': course.CourseName,
            'teacher': course.TeacherID.PersonID.PersianLastName if course.TeacherID else 'نامشخص',
            'exams': exam_list
        })

    return render(request, 'lms_web/student_exams.html', {
        'courses_data': courses_data,
        'student_name': f"{student.PersonID.PersianFirstName} {student.PersonID.PersianLastName}"
    })


# ==========================================
# بخش ویرایش و حذف مدارک
# ==========================================

@login_required(login_url='/login/')
def certificate_update_view(request, pk):
    if not request.user.is_superuser:
        return render(request, 'lms_web/403.html', status=403)

    cert = get_object_or_404(Certification, pk=pk)

    if request.method == 'POST':
        form = CertificationForm(request.POST, instance=cert)
        if form.is_valid():
            form.save()
            messages.success(request, 'مدرک با موفقیت ویرایش شد!')
            return redirect('certificate_list')
    else:
        form = CertificationForm(instance=cert)

    return render(request, 'lms_web/certificate_create.html', {'form': form, 'is_update': True})


@login_required(login_url='/login/')
def certificate_delete_view(request, pk):
    if not request.user.is_superuser:
        return render(request, 'lms_web/403.html', status=403)

    cert = get_object_or_404(Certification, pk=pk)

    if request.method == 'POST':
        # حذف ارتباط مدرک با اساتید (اگر وجود داشته باشه)
        TeacherCertification.objects.filter(CertificationID=cert).delete()
        cert.delete()
        messages.success(request, 'مدرک با موفقیت حذف شد!')
        return redirect('certificate_list')

    return render(request, 'lms_web/certificate_delete.html', {'cert': cert})


@login_required(login_url='/login/')
def my_enrollments_view(request):
    # پیدا کردن دانشجو بر اساس شماره تلفن یا ایمیل
    student = None
    if request.user.username:
        student = Student.objects.filter(PersonID__PhoneNumber=request.user.username).select_related('PersonID').first()

    if not student and request.user.email:
        student = Student.objects.filter(PersonID__EmailAddress=request.user.email).select_related('PersonID').first()

    if not student:
        messages.warning(request, 'اطلاعات دانشجویی برای این حساب کاربری یافت نشد.')
        return redirect('home')

    # گرفتن دوره‌هایی که این دانشجو توش ثبت‌نام کرده
    enrollments = StudentCourseTeacher.objects.filter(StudentID=student).select_related(
        'CourseID__TeacherID__PersonID',
        'TeacherID__PersonID'
    )

    return render(request, 'lms_web/my_enrollments.html', {
        'enrollments': enrollments,
        'student_name': f"{student.PersonID.PersianFirstName} {student.PersonID.PersianLastName}"
    })