from django.test import TestCase
from django.urls import reverse

from .models import Student


class StudentRegistrationTests(TestCase):
    def test_registration_page_is_available_at_canonical_and_legacy_urls(self):
        response = self.client.get(reverse('student_registration'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="student_id"')

        response = self.client.get(reverse('registration'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/Registration', follow=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/Registration/')
        self.assertRedirects(response, reverse('student_registration'))

    def test_registration_saves_student_and_shows_success_page(self):
        response = self.client.post(
            reverse('student_registration'),
            {
                'student_id': 'S-001',
                'first_name': 'Ada',
                'last_name': 'Lovelace',
                'gender': 'Female',
                'date_of_birth': '1815-12-10',
                'contact_number': '555-0100',
            },
        )

        self.assertRedirects(response, reverse('registration_success'))
        self.assertTrue(
            Student.objects.filter(
                student_id='S-001',
                contact_number='555-0100',
            ).exists()
        )
        self.assertContains(self.client.get(reverse('registration_success')), 'Registration Successful')

    def test_duplicate_student_id_shows_form_error_without_creating_another_student(self):
        Student.objects.create(
            student_id='S-001',
            first_name='Ada',
            last_name='Lovelace',
            gender='Female',
            date_of_birth='1815-12-10',
            contact_number='555-0100',
        )

        response = self.client.post(
            reverse('student_registration'),
            {
                'student_id': 'S-001',
                'first_name': 'Grace',
                'last_name': 'Hopper',
                'gender': 'Female',
                'date_of_birth': '1906-12-09',
                'contact_number': '555-0101',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A student with this ID is already registered.')
        self.assertContains(response, 'value="Grace"')
        self.assertEqual(Student.objects.filter(student_id='S-001').count(), 1)

    def test_directory_search_and_model_form_create(self):
        Student.objects.create(
            student_id='SRCC-TEST-001',
            first_name='Alex',
            last_name='Santos',
            gender='Male',
            date_of_birth='2004-02-15',
            contact_number='09170000001',
        )

        response = self.client.get(
            reverse('student_list'),
            {'q': 'sant'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SRCC-TEST-001')

        response = self.client.post(
            reverse('student_create'),
            {
                'student_id': 'SRCC-TEST-002',
                'first_name': 'Jamie',
                'last_name': 'Reyes',
                'gender': 'Female',
                'date_of_birth': '2003-11-08',
                'contact_number': '09170000002',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Student created successfully.')
        self.assertTrue(
            Student.objects.filter(student_id='SRCC-TEST-002').exists()
        )

    def test_update_saves_changes_and_shows_feedback(self):
        student = Student.objects.create(
            student_id='SRCC-TEST-003',
            first_name='Taylor',
            last_name='Cruz',
            gender='Female',
            date_of_birth='2004-06-21',
            contact_number='09170000003',
        )

        response = self.client.post(
            reverse('student_update', args=[student.pk]),
            {
                'student_id': student.student_id,
                'first_name': 'Taylor',
                'last_name': 'Rivera',
                'gender': 'Female',
                'date_of_birth': '2004-06-21',
                'contact_number': '09170000003',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Student updated successfully.')
        student.refresh_from_db()
        self.assertEqual(student.last_name, 'Rivera')

    def test_delete_requires_confirmation_and_post(self):
        student = Student.objects.create(
            student_id='SRCC-TEST-004',
            first_name='Morgan',
            last_name='Lee',
            gender='Other',
            date_of_birth='2004-01-01',
            contact_number='09170000004',
        )
        delete_url = reverse('student_delete', args=[student.pk])

        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Confirm deletion')
        self.assertTrue(Student.objects.filter(pk=student.pk).exists())

        response = self.client.post(delete_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Student deleted successfully.')
        self.assertFalse(Student.objects.filter(pk=student.pk).exists())
