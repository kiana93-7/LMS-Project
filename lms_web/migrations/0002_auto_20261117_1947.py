from django.db import migrations, models
import django.db.models.deletion  # <--- این خط رو حتماً اضافه کن

class Migration(migrations.Migration):

    dependencies = [
        ('lms_web', '0001_initial'), # اسم آخرین مایگریشن موفق قبلیت رو بذار (مثلاً 0001_initial)
    ]

    operations = [
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Title', models.CharField(max_length=100, verbose_name='عنوان آزمون')),
                ('ExamDate', models.DateField(blank=True, null=True, verbose_name='تاریخ آزمون')),
                ('TotalScore', models.PositiveSmallIntegerField(default=100, verbose_name='نمره کل')),
                ('Course', models.ForeignKey(db_column='Course_id', on_delete=django.db.models.deletion.CASCADE, to='lms_web.course', to_field='ID', verbose_name='دوره')),
            ],
            options={
                'db_table': 'lms_web_exam',
            },
        ),
        migrations.CreateModel(
            name='ExamScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Score', models.FloatField(verbose_name='نمره کسب شده')),
                ('Exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lms_web.exam', verbose_name='آزمون')),
                ('Student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lms_web.student', verbose_name='دانشجو')),
            ],
            options={
                'unique_together': {('Exam', 'Student')},
            },
        ),
    ]