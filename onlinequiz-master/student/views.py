from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.db.models import Sum, Count
from django.http import HttpResponseRedirect
from django.contrib import messages
from datetime import datetime, timedelta
import csv
from . import forms, models
from quiz import models as QMODEL
from teacher import models as TMODEL

def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'student/studentclick.html')

def student_signup_view(request):
    userForm = forms.StudentUserForm()
    studentForm = forms.StudentForm()
    mydict = {'userForm': userForm, 'studentForm': studentForm}
    
    if request.method == 'POST':
        userForm = forms.StudentUserForm(request.POST)
        studentForm = forms.StudentForm(request.POST, request.FILES)
        if userForm.is_valid() and studentForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            student = studentForm.save(commit=False)
            student.user = user
            student.save()
            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
            messages.success(request, 'Registration successful! Please login.')
            return HttpResponseRedirect('studentlogin')
        else:
            messages.error(request, 'Please correct the errors below.')
    
    return render(request, 'student/studentsignup.html', context=mydict)

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    student = models.Student.objects.get(user_id=request.user.id)
    total_courses = QMODEL.Course.objects.count()
    total_questions = QMODEL.Question.objects.count()
    
    # Get recent exam results
    recent_results = QMODEL.Result.objects.filter(
        student=student
    ).order_by('-date')[:5]
    
    # Calculate overall progress
    total_exams = QMODEL.Result.objects.filter(student=student).count()
    passed_exams = QMODEL.Result.objects.filter(
        student=student,
        marks__gte=Sum('exam__total_marks') * 0.4
    ).count()
    
    progress_percentage = (passed_exams / total_exams * 100) if total_exams > 0 else 0
    
    context = {
        'total_course': total_courses,
        'total_question': total_questions,
        'recent_results': recent_results,
        'progress_percentage': round(progress_percentage),
        'total_exams': total_exams,
        'passed_exams': passed_exams
    }
    return render(request, 'student/student_dashboard.html', context=context)

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_exam_view(request):
    courses = QMODEL.Course.objects.all()
    student = models.Student.objects.get(user_id=request.user.id)
    results = QMODEL.Result.objects.filter(student=student)
    
    # Add completion status to courses
    for course in courses:
        course.completed = results.filter(exam=course).exists()
        if course.completed:
            result = results.get(exam=course)
            course.score = result.marks
            course.passed = result.marks >= (course.total_marks * 0.4)
    
    return render(request, 'student/student_exam.html', {'courses': courses})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def take_exam_view(request, pk):
    course = QMODEL.Course.objects.get(id=pk)
    total_questions = QMODEL.Question.objects.filter(course=course).count()
    
    # Check if student has already taken this exam
    student = models.Student.objects.get(user_id=request.user.id)
    if QMODEL.Result.objects.filter(student=student, exam=course).exists():
        messages.warning(request, 'You have already completed this exam.')
        return redirect('student-exam')
    
    context = {
        'course': course,
        'total_questions': total_questions,
    }
    return render(request, 'student/take_exam.html', context)

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def start_exam_view(request, pk):
    course = QMODEL.Course.objects.get(id=pk)
    questions = QMODEL.Question.objects.filter(course=course).order_by('?')[:course.question_number]
    
    if request.method == 'POST':
        marks = 0
        for q in questions:
            selected_ans = request.POST.get(str(q.id))
            if selected_ans == q.answer:
                marks += q.marks
        
        student = models.Student.objects.get(user_id=request.user.id)
        result = QMODEL.Result.objects.create(
            student=student,
            exam=course,
            marks=marks
        )
        
        return redirect('view-result')
    
    context = {
        'course': course,
        'questions': questions,
        'time_left': course.question_number * 2 * 60  # 2 minutes per question in seconds
    }
    return render(request, 'student/start_exam.html', context)

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def view_result_view(request):
    student = models.Student.objects.get(user_id=request.user.id)
    results = QMODEL.Result.objects.filter(student=student).order_by('-date')
    
    # Add pass/fail status to results
    for result in results:
        result.passed = result.marks >= (result.exam.total_marks * 0.4)
        result.percentage = (result.marks / result.exam.total_marks) * 100
    
    return render(request, 'student/view_result.html', {'results': results})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_marks_view(request):
    student = models.Student.objects.get(user_id=request.user.id)
    results = QMODEL.Result.objects.filter(student=student)
    
    total_marks = sum(result.marks for result in results)
    total_exams = results.count()
    average_score = total_marks / total_exams if total_exams > 0 else 0
    
    context = {
        'results': results,
        'total_marks': total_marks,
        'total_exams': total_exams,
        'average_score': round(average_score, 2)
    }
    return render(request, 'student/student_marks.html', context)

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def check_marks_view(request, pk):
    course = QMODEL.Course.objects.get(id=pk)
    student = models.Student.objects.get(user_id=request.user.id)
    results = QMODEL.Result.objects.all().filter(exam=course).filter(student=student)
    return render(request, 'student/check_marks.html', {'results': results})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def calculate_marks_view(request):
    if request.COOKIES.get('course_id') is not None:
        course_id = request.COOKIES.get('course_id')
        course = QMODEL.Course.objects.get(id=course_id)
        
        total_marks = 0
        questions = QMODEL.Question.objects.all().filter(course=course)
        for i in range(len(questions)):
            
            selected_ans = request.COOKIES.get(str(i+1))
            actual_answer = questions[i].answer
            if selected_ans == actual_answer:
                total_marks = total_marks + questions[i].marks
        student = models.Student.objects.get(user_id=request.user.id)
        result = QMODEL.Result()
        result.marks = total_marks
        result.exam = course
        result.student = student
        result.save()

        return HttpResponseRedirect('view-result')

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def upload_csv_view(request):
    if request.method == 'POST':
        try:
            csv_file = request.FILES['csv_file']
            course_id = request.POST.get('course')
            course = QMODEL.Course.objects.get(id=course_id)
            
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Please upload a CSV file.')
                return redirect('upload-csv')
            
            decoded_file = csv_file.read().decode('utf-8')
            csv_data = csv.DictReader(decoded_file.splitlines())
            
            questions_added = 0
            for row in csv_data:
                try:
                    question = QMODEL.Question(
                        course=course,
                        marks=int(row['marks']),
                        question=row['question_text'],
                        option1=row['option1'],
                        option2=row['option2'],
                        option3=row['option3'],
                        option4=row['option4'],
                        answer=row['correct_answer']
                    )
                    question.save()
                    questions_added += 1
                except Exception as e:
                    messages.warning(request, f'Error processing row: {str(e)}')
                    continue
            
            messages.success(request, f'Successfully added {questions_added} questions to {course.course_name}')
            return redirect('student-exam')
            
        except Exception as e:
            messages.error(request, f'Error processing CSV file: {str(e)}')
            return redirect('upload-csv')
    
    courses = QMODEL.Course.objects.all()
    return render(request, 'student/upload_csv.html', {'courses': courses})