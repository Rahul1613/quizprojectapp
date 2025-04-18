from django.shortcuts import render, redirect, reverse
from . import forms, models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from datetime import date, datetime, timedelta
from quiz import models as QMODEL
from student import models as SMODEL
from quiz import forms as QFORM
from student.models import ExamNotification, Student
import sqlite3
from django.contrib import messages
import csv
import io

def teacherclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'teacher/teacherclick.html')

def teacher_signup_view(request):
    userForm=forms.TeacherUserForm()
    teacherForm=forms.TeacherForm()
    mydict={'userForm':userForm,'teacherForm':teacherForm}
    if request.method=='POST':
        userForm=forms.TeacherUserForm(request.POST)
        teacherForm=forms.TeacherForm(request.POST,request.FILES)
        if userForm.is_valid() and teacherForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            teacher=teacherForm.save(commit=False)
            teacher.user=user
            teacher.save()
            my_teacher_group = Group.objects.get_or_create(name='TEACHER')
            my_teacher_group[0].user_set.add(user)
        return HttpResponseRedirect('teacherlogin')
    return render(request,'teacher/teachersignup.html',context=mydict)

def is_teacher(user):
    return user.groups.filter(name='TEACHER').exists()

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_dashboard_view(request):
    # Get total slots count
    conn = sqlite3.connect('exam_slots.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM exam_slots')
    total_slots = c.fetchone()[0]
    conn.close()

    dict={
        'total_course':QMODEL.Course.objects.all().count(),
        'total_question':QMODEL.Question.objects.all().count(),
        'total_student':SMODEL.Student.objects.all().count(),
        'total_slots': total_slots
    }
    return render(request,'teacher/teacher_dashboard.html',context=dict)

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_exam_view(request):
    return render(request,'teacher/teacher_exam.html')

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_add_exam_view(request):
    courseForm=QFORM.CourseForm()
    if request.method=='POST':
        courseForm=QFORM.CourseForm(request.POST)
        if courseForm.is_valid():        
            course = courseForm.save(commit=False)
            course.save()

            # Create notifications for all students
            exam_date = datetime.strptime(request.POST.get('exam_date'), '%Y-%m-%d %H:%M')
            students = Student.objects.all()
            for student in students:
                notification = ExamNotification.objects.create(
                    student=student,
                    exam_name=course.course_name,
                    exam_date=exam_date,
                    message=f"New exam '{course.course_name}' has been scheduled for {exam_date.strftime('%B %d, %Y at %I:%M %p')}. Please prepare accordingly."
                )

            return HttpResponseRedirect('/teacher/teacher-view-exam')
    return render(request,'teacher/teacher_add_exam.html',{'courseForm':courseForm})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_exam_view(request):
    courses = QMODEL.Course.objects.all()
    return render(request,'teacher/teacher_view_exam.html',{'courses':courses})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def delete_exam_view(request, pk):
    try:
        course = QMODEL.Course.objects.get(id=pk)
        course.delete()
        return HttpResponseRedirect('/teacher/teacher-view-exam')
    except QMODEL.Course.DoesNotExist:
        return HttpResponseRedirect('/teacher/teacher-view-exam')  

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_question_view(request):
    return render(request,'teacher/teacher_question.html')

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_add_question_view(request):
    questionForm=QFORM.QuestionForm()
    if request.method=='POST':
        questionForm=QFORM.QuestionForm(request.POST)
        if questionForm.is_valid():
            question=questionForm.save(commit=False)
            course=QMODEL.Course.objects.get(id=request.POST.get('courseID'))
            question.course=course
            question.save()       
        return HttpResponseRedirect('/teacher/teacher-view-question')
    return render(request,'teacher/teacher_add_question.html',{'questionForm':questionForm})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_question_view(request):
    courses= QMODEL.Course.objects.all()
    return render(request,'teacher/teacher_view_question.html',{'courses':courses})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def see_question_view(request,pk):
    questions=QMODEL.Question.objects.all().filter(course_id=pk)
    return render(request,'teacher/see_question.html',{'questions':questions})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def remove_question_view(request,pk):
    question=QMODEL.Question.objects.get(id=pk)
    question.delete()
    return HttpResponseRedirect('/teacher/teacher-view-question')

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def book_exam_slot(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        subject = request.POST.get('subject')
        
        # Create exam slot
        exam_slot = models.ExamSlot.objects.create(
            teacher=models.Teacher.objects.get(user=request.user),
            date=date,
            start_time=start_time,
            end_time=end_time,
            subject=subject
        )
        
        # Create notifications for all students
        students = Student.objects.all()
        for student in students:
            ExamNotification.objects.create(
                student=student,
                exam_name=subject,
                exam_date=date,
                message=f"New exam '{subject}' has been scheduled for {date} from {start_time} to {end_time}. Please prepare accordingly."
            )
        
        return redirect('teacher-dashboard')
    
    slots = models.ExamSlot.objects.filter(teacher=models.Teacher.objects.get(user=request.user))
    return render(request, 'teacher/exam_slots.html', {'slots': slots})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def upload_questions_csv_view(request):
    if request.method == 'POST':
        form = forms.TeacherCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            course = form.cleaned_data['course']
            
            # Check if file is CSV
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Please upload a CSV file')
                return redirect('upload-questions-csv')
            
            # Read CSV file
            try:
                csv_data = csv_file.read().decode('utf-8')
                csv_io = io.StringIO(csv_data)
                reader = csv.DictReader(csv_io)
                
                # Validate CSV structure
                required_fields = ['question', 'option1', 'option2', 'option3', 'option4', 'answer', 'marks']
                csv_fields = reader.fieldnames
                
                if not all(field in csv_fields for field in required_fields):
                    messages.error(request, 'CSV file must contain all required fields: ' + ', '.join(required_fields))
                    return redirect('upload-questions-csv')
                
                questions_added = 0
                # Process each row
                for row in reader:
                    # Validate answer
                    answer = row['answer'].strip()
                    if answer not in ['Option1', 'Option2', 'Option3', 'Option4']:
                        continue
                    
                    try:
                        marks = int(row['marks'])
                    except ValueError:
                        marks = 1  # Default to 1 mark if invalid
                    
                    # Create question
                    QMODEL.Question.objects.create(
                        course=course,
                        marks=marks,
                        question=row['question'],
                        option1=row['option1'],
                        option2=row['option2'],
                        option3=row['option3'],
                        option4=row['option4'],
                        answer=answer
                    )
                    questions_added += 1
                
                messages.success(request, f'{questions_added} questions uploaded successfully!')
                return redirect('teacher-view-question')
                
            except Exception as e:
                messages.error(request, f'Error processing CSV file: {str(e)}')
                return redirect('upload-questions-csv')
    else:
        form = forms.TeacherCSVUploadForm()
    return render(request, 'teacher/upload_questions_csv.html', {'form': form})
