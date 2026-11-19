from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Student


class StudentRegistrationTests(TestCase):
    def setUp(self):
        staff_user = get_user_model().objects.create_user(
            username='teststaff',
            password='Test-Staff-2026',
            is_staff=True,
        )
        self.client.force_login(staff_user)

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


class StaffAuthenticationTests(TestCase):
    def setUp(self):
        self.staff_user = get_user_model().objects.create_user(
            username='staff',
            password='Test-Staff-2026',
            is_staff=True,
        )
        self.normal_user = get_user_model().objects.create_user(
            username='student',
            password='Test-Student-2026',
            is_staff=False,
        )

    def test_login_page_is_public_and_invalid_login_fails(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse('login'),
            {'username': 'staff', 'password': 'wrong-password'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')

    def test_staff_login_dashboard_and_logout(self):
        response = self.client.post(
            reverse('login'),
            {'username': 'staff', 'password': 'Test-Staff-2026'},
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('staff_dashboard'),
        )
        self.assertContains(response, 'Welcome, staff!')

        response = self.client.post(reverse('logout'), follow=True)
        self.assertRedirects(response, reverse('login'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_protected_views_require_staff_access(self):
        protected_urls = [
            reverse('staff_dashboard'),
            reverse('student_list'),
            reverse('student_create'),
        ]

        for url in protected_urls:
            response = self.client.get(url)
            self.assertRedirects(
                response,
                f"{reverse('login')}?next={url}",
            )

        self.client.force_login(self.normal_user)
        for url in protected_urls:
            response = self.client.get(url)
            self.assertRedirects(
                response,
                f"{reverse('login')}?next={url}",
            )

    def test_dashboard_summaries_and_search(self):
        self.client.force_login(self.staff_user)
        Student.objects.create(
            student_id='DASH-001',
            first_name='Ada',
            last_name='Lovelace',
            gender='Female',
            date_of_birth='1815-12-10',
            contact_number='555-0101',
        )
        Student.objects.create(
            student_id='DASH-002',
            first_name='Grace',
            last_name='Hopper',
            gender='Female',
            date_of_birth='1906-12-09',
            contact_number='555-0102',
        )
        Student.objects.create(
            student_id='DASH-003',
            first_name='Alan',
            last_name='Turing',
            gender='Male',
            date_of_birth='1912-06-23',
            contact_number='555-0103',
        )

        response = self.client.get(
            reverse('staff_dashboard'),
            {'q': 'ada'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_students'], 3)
        self.assertEqual(response.context['male_students'], 1)
        self.assertEqual(response.context['female_students'], 2)
        self.assertAlmostEqual(response.context['male_percent'], 100 / 3)
        self.assertAlmostEqual(response.context['female_percent'], 200 / 3)
        self.assertEqual(
            list(response.context['students'].values_list('student_id', flat=True)),
            ['DASH-001'],
        )
        self.assertContains(response, '555-0101')

    def test_dashboard_percentages_are_zero_without_students(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('staff_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_students'], 0)
        self.assertEqual(response.context['male_percent'], 0)
        self.assertEqual(response.context['female_percent'], 0)
        self.assertContains(response, 'No student records found.')
