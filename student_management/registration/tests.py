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
