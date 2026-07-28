from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import StudentProfile, Education, Certificate
from apps.applications.models import Application
from apps.interviews.models import Interview
from .forms import StudentProfileForm, ResumeUploadForm, SkillsForm, EducationForm, CertificateForm

@login_required
def student_list(request):
    # Only companies or admin/officers can list students
    if request.user.role == 'student':
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')
    
    students = StudentProfile.objects.all()
    
    # Filter by search
    query = request.GET.get('q')
    if query:
        students = students.filter(
            user__first_name__icontains=query
        ) | students.filter(
            user__last_name__icontains=query
        ) | students.filter(
            roll_number__icontains=query
        ) | students.filter(
            skills__icontains=query
        )
        
    return render(request, 'students/student_list.html', {'students': students})

@login_required
def student_detail(request, pk):
    # Retrieve student profile
    student = get_object_or_404(StudentProfile, pk=pk)
    
    # Check permissions: user can view their own profile, or admins/companies can view
    if request.user.role == 'student' and request.user.student_profile != student:
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')
        
    context = {
        'student': student,
        'education_history': student.education_history.all(),
        'certificates': student.certificates.all(),
    }
    return render(request, 'students/student_detail.html', context)

@login_required
def student_create(request):
    if request.user.role != 'admin' and request.user.role != 'officer':
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = StudentProfileForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Student profile created.")
            return redirect('students:student_list')
    else:
        form = StudentProfileForm()
    return render(request, 'students/student_create.html', {'form': form})

@login_required
def student_update(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)
    if request.user.role == 'student' and request.user.student_profile != student:
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')
        
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile details updated.")
            return redirect('students:student_detail', pk=student.pk)
    else:
        form = StudentProfileForm(instance=student)
    return render(request, 'students/student_update.html', {'form': form, 'student': student})

@login_required
def student_delete(request, pk):
    if request.user.role not in ['admin', 'officer']:
        messages.error(request, "Access denied.")
        return redirect('dashboard:home')
    student = get_object_or_404(StudentProfile, pk=pk)
    if request.method == 'POST':
        student.user.delete() # Deleting user deletes profile
        messages.success(request, "Student deleted successfully.")
        return redirect('students:student_list')
    return render(request, 'students/student_delete.html', {'student': student})

@login_required
def resume_upload(request):
    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, "Complete profile registration first.")
        return redirect('accounts:edit_profile')
        
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Resume uploaded successfully.")
            return redirect('accounts:profile')
    else:
        form = ResumeUploadForm(instance=student)
    return render(request, 'students/resume_upload.html', {'form': form})

@login_required
def skills_view(request):
    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, "Complete profile registration first.")
        return redirect('accounts:edit_profile')
        
    if request.method == 'POST':
        form = SkillsForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Skills updated successfully.")
            return redirect('accounts:profile')
    else:
        form = SkillsForm(instance=student)
    return render(request, 'students/skills.html', {'form': form})

@login_required
def education_view(request):
    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        return redirect('accounts:edit_profile')
        
    history = student.education_history.all()
    
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            edu = form.save(commit=False)
            edu.student = student
            edu.save()
            messages.success(request, "Education entry added.")
            return redirect('students:education')
    else:
        form = EducationForm()
        
    return render(request, 'students/education.html', {'form': form, 'history': history})

@login_required
def certificates_view(request):
    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        return redirect('accounts:edit_profile')
        
    certificates = student.certificates.all()
    
    if request.method == 'POST':
        form = CertificateForm(request.POST, request.FILES)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.student = student
            cert.save()
            messages.success(request, "Certificate added successfully.")
            return redirect('students:certificates')
    else:
        form = CertificateForm()
        
    return render(request, 'students/certificates.html', {'form': form, 'certificates': certificates})

@login_required
def applied_jobs(request):
    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        return redirect('accounts:edit_profile')
        
    applications = Application.objects.filter(student=student)
    return render(request, 'students/applied_jobs.html', {'applications': applications})

@login_required
def shortlisted_jobs(request):
    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        return redirect('accounts:edit_profile')
        
    applications = Application.objects.filter(student=student, status='shortlisted')
    return render(request, 'students/shortlisted_jobs.html', {'applications': applications})

@login_required
def interview_schedule(request):
    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        return redirect('accounts:edit_profile')
        
    interviews = Interview.objects.filter(application__student=student).order_by('interview_date')
    return render(request, 'students/interview_schedule.html', {'interviews': interviews})

@login_required
def placement_status(request):
    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        return redirect('accounts:edit_profile')
        
    if request.method == 'POST' and request.user.role in ['admin', 'officer']:
        status = request.POST.get('status')
        if status in ['unplaced', 'shortlisted', 'placed']:
            student.placement_status = status
            student.save()
            messages.success(request, f"Placement status updated to {status.capitalize()}.")
        return redirect('students:student_detail', pk=student.pk)
        
    return render(request, 'students/placement_status.html', {'student': student})
