from django.db import models
from django.contrib.auth.models import User

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/Teacher/', null=True, blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20, null=False)
    status = models.BooleanField(default=False)
    salary = models.PositiveIntegerField(null=True)

    @property
    def get_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def get_instance(self):
        return self

    def __str__(self):
        return self.user.first_name


class Course(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=255)

    def __str__(self):
        return self.course_name


class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    question = models.CharField(max_length=500)
    option1 = models.CharField(max_length=100)
    option2 = models.CharField(max_length=100)
    option3 = models.CharField(max_length=100)
    option4 = models.CharField(max_length=100)
    answer = models.CharField(max_length=10)
    marks = models.IntegerField(default=1)

    def __str__(self):
        return self.question


class ExamSlot(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    date = models.DateTimeField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    subject = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.subject} - {self.date}"


class ExamNotification(models.Model):
    student = models.ForeignKey('student.Student', on_delete=models.CASCADE)
    exam_name = models.CharField(max_length=255)
    exam_date = models.DateTimeField()
    message = models.TextField()

    def __str__(self):
        return f"Notification for {self.exam_name}"
