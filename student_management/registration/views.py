
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import StudentForm
from .models import Student


# Student Registration
def student_registration(request):
    form = StudentForm(request.POST or None)
    error = None

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        if Student.objects.filter(student_id=student_id).exists():
            error = 'A student with this ID is already registered.'
            form.add_error('student_id', error)
        elif form.is_valid():
            form.save()
            messages.success(
                request,
                'Student registered successfully.'
            )
            return redirect('registration_success')
        else:
            error = '; '.join(
                message
                for field_errors in form.errors.values()
                for message in field_errors
            )

    return render(
        request,
        'registration/student_registration.html',
        {
            'form': form,
            'form_values': request.POST,
            'error': error,
        }
    )


# Registration Success
def registration_success(request):
    return render(
        request,
        'registration/registration_success.html'
    )


# Student Directory and Search
def student_list(request):
    query = request.GET.get('q', '').strip()

    students = Student.objects.all().order_by(
        'last_name',
        'first_name'
    )

    if query:
        students = students.filter(
            Q(student_id__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

    return render(
        request,
        'registration/student_list.html',
        {
            'students': students,
            'query': query
        }
    )


# Create Student
def student_create(request):
    form = StudentForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        student = form.save()

        messages.success(
            request,
            'Student created successfully.'
        )

        return redirect('student_list')

    return render(
        request,
        'registration/student_form.html',
        {
            'form': form,
            'page_title': 'Create Student'
        }
    )


# Student Details
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)

    return render(
        request,
        'registration/student_detail.html',
        {'student': student}
    )


# Update Student
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)

    form = StudentForm(
        request.POST or None,
        instance=student
    )

    if request.method == 'POST' and form.is_valid():
        form.save()

        messages.success(
            request,
            'Student updated successfully.'
        )

        return redirect(
            'student_detail',
            pk=student.pk
        )

    return render(
        request,
        'registration/student_form.html',
        {
            'form': form,
            'page_title': 'Edit Student',
            'student': student
        }
    )


# Delete Student
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        student.delete()

        messages.success(
            request,
            'Student deleted successfully.'
        )

        return redirect('student_list')

    return render(
        request,
        'registration/student_confirm_delete.html',
        {'student': student}
    )
    