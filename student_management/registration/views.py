from django.db import IntegrityError, transaction
from django.shortcuts import render, redirect
from .models import Student


def student_registration(request):
    form_values = {}
    if request.method == 'POST':
        form_values = request.POST
        student_id = request.POST.get('student_id')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        date_of_birth = request.POST.get('date_of_birth')
        contact_number = request.POST.get('contact_number')

        try:
            with transaction.atomic():
                Student.objects.create(
                    student_id=student_id,
                    first_name=first_name,
                    last_name=last_name,
                    gender=gender,
                    date_of_birth=date_of_birth,
                    contact_number=contact_number
                )
        except IntegrityError:
            if not Student.objects.filter(student_id=student_id).exists():
                raise
            return render(
                request,
                'registration/student_registration.html',
                {
                    'form_values': form_values,
                    'error': 'A student with this ID is already registered. Please use a different student ID.',
                },
            )

        return redirect('registration_success')

    return render(
        request,
        'registration/student_registration.html',
        {'form_values': form_values},
    )

def registration_success(request):
    return render(request, 'registration/registration_success.html')