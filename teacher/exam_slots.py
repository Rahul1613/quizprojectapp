from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import connection
import sqlite3
from datetime import datetime, date
from student.models import ExamNotification, Student
from .models import Teacher

def init_exam_slots_db():
    conn = sqlite3.connect('exam_slots.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS exam_slots
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  teacher_id INTEGER NOT NULL,
                  date DATE NOT NULL,
                  start_time TIME NOT NULL,
                  end_time TIME NOT NULL,
                  subject TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def delete_expired_slots():
    current_date = date.today()
    current_time = datetime.now().strftime('%H:%M')
    
    conn = sqlite3.connect('exam_slots.db')
    c = conn.cursor()
    
    # Get expired slots for notification
    c.execute('''SELECT * FROM exam_slots 
                WHERE date < ? OR 
                (date = ? AND end_time < ?)''',
             (current_date, current_date, current_time))
    expired_slots = c.fetchall()
    
    # Delete expired slots
    c.execute('''DELETE FROM exam_slots 
                WHERE date < ? OR 
                (date = ? AND end_time < ?)''',
             (current_date, current_date, current_time))
    conn.commit()
    conn.close()
    
    return expired_slots

@login_required(login_url='teacherlogin')
def exam_slots_view(request):
    teacher_id = request.user.id
    teacher_user = request.user
    teacher = Teacher.objects.get(user=teacher_user)
    
    # Delete expired slots first
    expired_slots = delete_expired_slots()
    
    if request.method == 'POST':
        if 'delete_slot' in request.POST:
            slot_id = request.POST.get('slot_id')
            conn = sqlite3.connect('exam_slots.db')
            c = conn.cursor()
            
            # Check if the slot belongs to the current teacher
            c.execute('SELECT teacher_id FROM exam_slots WHERE id = ?', (slot_id,))
            slot = c.fetchone()
            
            if slot and slot[0] == teacher_id:
                c.execute('DELETE FROM exam_slots WHERE id = ?', (slot_id,))
                conn.commit()
                messages.success(request, 'Slot deleted successfully!')
            else:
                messages.error(request, 'You can only delete your own slots!')
            
            conn.close()
            return redirect('exam-slots')
            
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        subject = request.POST.get('subject')

        # Validate that the slot is not in the past
        slot_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
        if slot_datetime < datetime.now():
            messages.error(request, 'Cannot book slots in the past!')
            return redirect('exam-slots')

        conn = sqlite3.connect('exam_slots.db')
        c = conn.cursor()
        
        # Check for existing bookings
        c.execute('''SELECT * FROM exam_slots 
                    WHERE date = ? AND 
                    ((start_time <= ? AND end_time >= ?) OR
                     (start_time <= ? AND end_time >= ?))''',
                 (date, start_time, start_time, end_time, end_time))
        existing_slot = c.fetchone()

        if existing_slot:
            messages.error(request, 'This time slot is already booked!')
        else:
            c.execute('''INSERT INTO exam_slots (teacher_id, date, start_time, end_time, subject)
                        VALUES (?, ?, ?, ?, ?)''',
                     (teacher_id, date, start_time, end_time, subject))
            conn.commit()
            
            # Create notifications for all students
            students = Student.objects.all()
            exam_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
            teacher_name = f"{teacher_user.first_name} {teacher_user.last_name}"
            if not teacher_name.strip():  # If teacher name is empty
                teacher_name = teacher_user.username
                
            for student in students:
                ExamNotification.objects.create(
                    student=student,
                    exam_name=subject,
                    exam_date=exam_datetime,
                    message=f"Professor {teacher_name} has scheduled a test for '{subject}' on {exam_datetime.strftime('%B %d, %Y')} from {start_time} to {end_time}. Please be prepared for the examination."
                )
            
            messages.success(request, 'Slot booked successfully!')
        
        conn.close()
        return redirect('exam-slots')

    # Get all slots for display
    conn = sqlite3.connect('exam_slots.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''SELECT * FROM exam_slots 
                ORDER BY date, start_time''')
    slots = c.fetchall()
    conn.close()
    
    # Convert slots to list of dictionaries for template
    slots_list = []
    for slot in slots:
        slot_dict = dict(slot)
        # Add a flag to indicate if the slot belongs to the current teacher
        slot_dict['is_owner'] = (slot_dict['teacher_id'] == teacher_id)
        slots_list.append(slot_dict)
    
    return render(request, 'teacher/exam_slots.html', {'slots': slots_list})

@login_required(login_url='teacherlogin')
def teacher_slots_view(request):
    teacher = request.user.id
    
    # Delete expired slots first
    delete_expired_slots()
    
    conn = sqlite3.connect('exam_slots.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM exam_slots WHERE teacher_id = ? ORDER BY date, start_time', (teacher,))
    slots = c.fetchall()
    conn.close()
    return render(request, 'teacher/teacher_slots.html', {'slots': slots})

# Initialize the database when the module is loaded
init_exam_slots_db()
