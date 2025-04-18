from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group, User
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta, datetime
from quiz import models as QMODEL
from teacher import models as TMODEL
from .models import ExamNotification, Student
from django.core.exceptions import ObjectDoesNotExist
import csv
import io
from django.contrib import messages
from collections import defaultdict

#for showing signup/login button for student
def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'student/studentclick.html')

def student_signup_view(request):
    userForm=forms.StudentUserForm()
    studentForm=forms.StudentForm()
    mydict={'userForm':userForm,'studentForm':studentForm}
    if request.method=='POST':
        userForm=forms.StudentUserForm(request.POST)
        studentForm=forms.StudentForm(request.POST,request.FILES)
        if userForm.is_valid() and studentForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            student=studentForm.save(commit=False)
            student.user=user
            student.save()
            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
        return HttpResponseRedirect('studentlogin')
    return render(request,'student/studentsignup.html',context=mydict)

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    dict = {}
    student = Student.objects.get(user=request.user)
    
    # Get current time
    current_time = datetime.now()
    one_day_ago = current_time - timedelta(days=1)
    
    # Delete notifications older than 24 hours
    ExamNotification.objects.filter(created_at__lt=one_day_ago).delete()
    
    # Get recent notifications
    dict['notifications'] = ExamNotification.objects.filter(
        student=student,
        created_at__gte=one_day_ago
    ).order_by('-created_at')[:5]
    
    dict['total_course'] = QMODEL.Course.objects.all().count()
    dict['total_question'] = QMODEL.Question.objects.all().count()
    return render(request,'student/student_dashboard.html',context=dict)

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_exam_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/student_exam.html',{'courses':courses})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def take_exam_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    total_questions=QMODEL.Question.objects.all().filter(course=course).count()
    questions=QMODEL.Question.objects.all().filter(course=course)
    total_marks=0
    for q in questions:
        total_marks=total_marks + q.marks
    
    return render(request,'student/take_exam.html',{'course':course,'total_questions':total_questions,'total_marks':total_marks})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def start_exam_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    questions=QMODEL.Question.objects.all().filter(course=course)
    if request.method=='POST':
        pass
    response= render(request,'student/start_exam.html',{'course':course,'questions':questions})
    response.set_cookie('course_id',course.id)
    return response

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def calculate_marks_view(request):
    if request.COOKIES.get('course_id') is not None:
        course_id = request.COOKIES.get('course_id')
        try:
            course = QMODEL.Course.objects.get(id=course_id)
            total_marks = 0
            questions = QMODEL.Question.objects.all().filter(course=course)
            selected_answers = {}  # Dictionary to store selected answers
            
            for i in range(len(questions)):
                selected_ans = request.COOKIES.get(str(i+1))
                actual_answer = questions[i].answer
                selected_answers[str(questions[i].id)] = selected_ans  # Store the selected answer
                
                if selected_ans == actual_answer:
                    total_marks += questions[i].marks
            
            student = Student.objects.get(user_id=request.user.id)
            result = QMODEL.Result.objects.create(
                marks=total_marks,
                exam=course,
                student=student,
                selected_answers=selected_answers  # Save selected answers in the result
            )

            # Redirect to exam report page
            return HttpResponseRedirect(f'/student/exam-report/{course_id}')
        except ObjectDoesNotExist:
            return HttpResponseRedirect('student-dashboard')
    return HttpResponseRedirect('student-dashboard')

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def view_result_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/view_result.html',{'courses':courses})
    
@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def check_marks_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    student = Student.objects.get(user_id=request.user.id)
    results= QMODEL.Result.objects.all().filter(exam=course).filter(student=student)
    return render(request,'student/check_marks.html',{
        'results': results,
        'course': course,
        'has_report': True  # Add this to indicate that a detailed report is available
    })

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_marks_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/student_marks.html',{'courses':courses})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def view_notifications(request):
    student = Student.objects.get(user=request.user)
    
    # Get current time
    current_time = datetime.now()
    one_day_ago = current_time - timedelta(days=1)
    
    # Delete notifications older than 24 hours
    ExamNotification.objects.filter(created_at__lt=one_day_ago).delete()
    
    # Get remaining notifications
    notifications = ExamNotification.objects.filter(
        student=student,
        created_at__gte=one_day_ago
    ).order_by('-created_at')
    
    # Mark notifications as read
    unread_notifications = notifications.filter(is_read=False)
    unread_notifications.update(is_read=True)
    
    return render(request, 'student/notifications.html', {'notifications': notifications})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_notifications_view(request):
    student = Student.objects.get(user=request.user)
    notifications = ExamNotification.objects.filter(student=student)
    
    # Mark all notifications as read
    unread_notifications = notifications.filter(is_read=False)
    unread_notifications.update(is_read=True)
    
    return render(request, 'student/notifications.html', {
        'notifications': notifications,
        'unread_count': unread_notifications.count()
    })

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def upload_csv_view(request):
    if request.method == 'POST':
        form = forms.CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            course = form.cleaned_data['course']
            
            # Check if file is CSV
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Please upload a CSV file')
                return redirect('upload-csv')
            
            # Read CSV file
            try:
                csv_data = csv_file.read().decode('utf-8')
                csv_io = io.StringIO(csv_data)
                reader = csv.DictReader(csv_io)
                
                # Validate CSV structure
                required_fields = ['question', 'option1', 'option2', 'option3', 'option4', 'answer']
                csv_fields = reader.fieldnames
                
                if not all(field in csv_fields for field in required_fields):
                    messages.error(request, 'CSV file must contain all required fields: ' + ', '.join(required_fields))
                    return redirect('upload-csv')
                
                # Process each row
                for row in reader:
                    # Validate answer
                    answer = row['answer'].strip()
                    if answer not in ['Option1', 'Option2', 'Option3', 'Option4']:
                        continue
                    
                    # Create question
                    QMODEL.Question.objects.create(
                        course=course,
                        marks=1,  # Default mark per question
                        question=row['question'],
                        option1=row['option1'],
                        option2=row['option2'],
                        option3=row['option3'],
                        option4=row['option4'],
                        answer=answer
                    )
                
                messages.success(request, 'Questions uploaded successfully!')
                return redirect('student-exam')
                
            except Exception as e:
                messages.error(request, f'Error processing CSV file: {str(e)}')
                return redirect('upload-csv')
    else:
        form = forms.CSVUploadForm()
    return render(request, 'student/upload_csv.html', {'form': form})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def generate_exam_report(request, course_id):
    try:
        course = QMODEL.Course.objects.get(id=course_id)
        student = Student.objects.get(user_id=request.user.id)
        result = QMODEL.Result.objects.filter(exam=course, student=student).order_by('-date').first()
        
        if not result:
            messages.error(request, "No result found for this exam.")
            return redirect('student-exam')
        
        questions = QMODEL.Question.objects.filter(course=course)
        total_questions = questions.count()
        correct_answers = []
        wrong_answers = []
        
        # Process answers using stored selected_answers
        for question in questions:
            selected_ans = result.selected_answers.get(str(question.id))
            if selected_ans == question.answer:
                correct_answers.append({
                    'question': question.question,
                    'submitted': selected_ans
                })
            else:
                wrong_answers.append({
                    'question': question.question,
                    'submitted': selected_ans or "Not answered",
                    'correct': question.answer
                })
        
        percentage = (result.marks / course.total_marks) * 100
        context = {
            'course': course,
            'result': result,
            'total_questions': total_questions,
            'correct_count': len(correct_answers),
            'wrong_count': len(wrong_answers),
            'percentage': percentage,
            'correct_answers': correct_answers,
            'wrong_answers': wrong_answers,
            'exam_date': result.date
        }
        
        return render(request, 'student/exam_report.html', context)
    except QMODEL.Course.DoesNotExist:
        messages.error(request, "Course not found.")
        return redirect('student-exam')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('student-exam')