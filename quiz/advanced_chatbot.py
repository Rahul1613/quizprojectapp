from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from quiz.models import *
from student.models import Student
from teacher.models import Teacher
import json
import re
from datetime import datetime, timedelta

class AdvancedQuizChatbot:
    def __init__(self):
        self.context = {}
        
    def get_user_info(self, user):
        """Get user type and relevant information"""
        try:
            if Student.objects.filter(user=user).exists():
                return "student", Student.objects.get(user=user)
            elif Teacher.objects.filter(user=user).exists():
                return "teacher", Teacher.objects.get(user=user)
            elif user.is_staff:
                return "admin", None
            return "unknown", None
        except:
            return "unknown", None

    def get_quiz_stats(self, user):
        """Get quiz statistics for users"""
        try:
            user_type, profile = self.get_user_info(user)
            if user_type == "student":
                total_quizzes = Result.objects.filter(student=profile).count()
                passed_quizzes = Result.objects.filter(student=profile, status="Pass").count()
                return {
                    "total_quizzes": total_quizzes,
                    "passed_quizzes": passed_quizzes,
                    "success_rate": f"{(passed_quizzes/total_quizzes)*100:.1f}%" if total_quizzes > 0 else "N/A"
                }
            elif user_type == "teacher":
                total_quizzes = Question.objects.filter(teacher=profile).count()
                total_students = Student.objects.filter(teacher=profile).count()
                return {
                    "total_quizzes_created": total_quizzes,
                    "total_students": total_students
                }
            return {}
        except:
            return {}

    def get_upcoming_quizzes(self, user):
        """Get upcoming quizzes for the user"""
        try:
            user_type, profile = self.get_user_info(user)
            if user_type == "student":
                courses = Course.objects.filter(student=profile)
                upcoming = []
                for course in courses:
                    quizzes = Quiz.objects.filter(course=course, end_time__gt=datetime.now())
                    for quiz in quizzes:
                        upcoming.append({
                            "course": course.course_name,
                            "quiz": quiz.quiz_name,
                            "date": quiz.end_time.strftime("%Y-%m-%d %H:%M")
                        })
                return upcoming
            return []
        except:
            return []

    def process_admin_query(self, query, user):
        """Handle admin-specific queries"""
        if "total users" in query:
            total_students = Student.objects.count()
            total_teachers = Teacher.objects.count()
            return f"Total Users: {total_students + total_teachers} (Students: {total_students}, Teachers: {total_teachers})"
        
        if "system stats" in query:
            total_courses = Course.objects.count()
            total_quizzes = Quiz.objects.count()
            total_questions = Question.objects.count()
            return f"System Statistics:\n- Courses: {total_courses}\n- Quizzes: {total_quizzes}\n- Questions: {total_questions}"
        
        return None

    def process_teacher_query(self, query, user):
        """Handle teacher-specific queries"""
        user_type, profile = self.get_user_info(user)
        if user_type != "teacher":
            return None

        if "my students" in query:
            students = Student.objects.filter(teacher=profile)
            return f"You have {students.count()} students enrolled."
        
        if "quiz stats" in query:
            stats = self.get_quiz_stats(user)
            return f"Your Quiz Statistics:\n- Total Quizzes Created: {stats['total_quizzes_created']}\n- Total Students: {stats['total_students']}"
        
        return None

    def process_student_query(self, query, user):
        """Handle student-specific queries"""
        user_type, profile = self.get_user_info(user)
        if user_type != "student":
            return None

        if "my progress" in query:
            stats = self.get_quiz_stats(user)
            return f"Your Progress:\n- Total Quizzes Taken: {stats['total_quizzes']}\n- Passed Quizzes: {stats['passed_quizzes']}\n- Success Rate: {stats['success_rate']}"
        
        if "upcoming quizzes" in query:
            upcoming = self.get_upcoming_quizzes(user)
            if not upcoming:
                return "You have no upcoming quizzes."
            response = "Your upcoming quizzes:\n"
            for quiz in upcoming:
                response += f"- {quiz['course']}: {quiz['quiz']} (Due: {quiz['date']})\n"
            return response
        
        return None

    def get_course_info(self, query):
        """Get information about specific courses"""
        courses = Course.objects.all()
        for course in courses:
            if course.course_name.lower() in query.lower():
                total_quizzes = Quiz.objects.filter(course=course).count()
                total_students = Student.objects.filter(course=course).count()
                return f"Course: {course.course_name}\n- Total Quizzes: {total_quizzes}\n- Enrolled Students: {total_students}"
        return None

    def process_query(self, query, user):
        """Main query processing function"""
        # Check user type specific queries first
        user_type, _ = self.get_user_info(user)
        
        # Process role-specific queries
        if user_type == "admin":
            admin_response = self.process_admin_query(query, user)
            if admin_response:
                return admin_response
                
        if user_type == "teacher":
            teacher_response = self.process_teacher_query(query, user)
            if teacher_response:
                return teacher_response
                
        if user_type == "student":
            student_response = self.process_student_query(query, user)
            if student_response:
                return student_response

        # Check for course-specific queries
        course_info = self.get_course_info(query)
        if course_info:
            return course_info

        # General queries
        responses = {
            "help": """I can help you with:
1. Quiz Information
2. Course Details
3. Personal Progress
4. Technical Support
5. System Navigation
6. Exam Rules and Guidelines
7. Schedule Information
8. Grade Information

What would you like to know more about?""",
            
            "quiz rules": """Quiz Rules:
1. Answer all questions within the time limit
2. No browser tab switching allowed
3. Each question has only one correct answer
4. You can review answers before final submission
5. Results are shown immediately after submission""",
            
            "how to start quiz": """To start a quiz:
1. Log in to your account
2. Select your course
3. Choose the available quiz
4. Read instructions carefully
5. Click 'Start Quiz' button
6. Timer will begin automatically""",
            
            "technical issues": """If you're having technical issues:
1. Check your internet connection
2. Clear browser cache
3. Use supported browsers (Chrome/Firefox)
4. Disable browser extensions
5. Contact support if problems persist""",
            
            "forgot password": """To reset your password:
1. Click 'Forgot Password' on login page
2. Enter your registered email
3. Check email for reset link
4. Create new password
5. Log in with new credentials""",
            
            "contact support": "For support, email: support@onlinequiz.com or use the help desk portal in your dashboard.",
            
            "browser support": "We recommend using latest versions of: Chrome, Firefox, Safari, or Edge.",
            
            "study tips": """Study Tips for Better Performance:
1. Review course materials regularly
2. Take practice quizzes
3. Study in short, focused sessions
4. Use flashcards for key concepts
5. Join study groups""",
        }

        # Check for matching keywords in general responses
        for key, response in responses.items():
            if key in query.lower():
                return response

        # Default response if no specific match found
        return "I'm here to help! You can ask me about:\n- Quiz rules and guidelines\n- Course information\n- Technical support\n- Study tips\n- Your progress\n\nPlease be more specific about what you'd like to know."

chatbot = AdvancedQuizChatbot()

@csrf_exempt
@require_http_methods(["POST"])
def advanced_chatbot_message(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        # Get response from chatbot
        response = chatbot.process_query(user_message, request.user)
        
        return JsonResponse({
            'status': 'success',
            'response': response
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
