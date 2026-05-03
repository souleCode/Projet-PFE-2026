from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from Apps.Cameras.models import Camera
from Apps.Users.models import User
from Apps.alertes.models import Alert
from .models import Audit, AuditCapture


class AuditWorkflowTests(APITestCase):
	def setUp(self):
		self.client = APIClient()
		self.user = User.objects.create_user(
			email='audit@example.com',
			password='password123',
			first_name='Audit',
			last_name='User',
			role='admin',
			is_staff=True,
		)
		self.camera = Camera.objects.create(
			name='CAM-01',
			location='Zone A',
			status='active',
			is_active=True,
		)
		self.alert = Alert.objects.create(
			camera=self.camera,
			epi_missing=['hardhat'],
			criticity='moyenne',
			status='nouveau',
		)
		self.client.force_authenticate(user=self.user)

	def test_cannot_create_second_active_audit_for_same_alert(self):
		Audit.objects.create(
			title='Audit existant',
			camera=self.camera,
			alert=self.alert,
			created_by=self.user,
			status='ouvert',
		)

		response = self.client.post(
			reverse('audit_list_create'),
			{
				'title': 'Second audit',
				'camera': self.camera.id,
				'alert': self.alert.id,
				'notes': 'Tentative de doublon',
			},
			format='json'
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(Audit.objects.count(), 1)

	def test_can_create_new_audit_when_previous_is_closed(self):
		Audit.objects.create(
			title='Audit clos',
			camera=self.camera,
			alert=self.alert,
			created_by=self.user,
			status='clos',
		)

		response = self.client.post(
			reverse('audit_list_create'),
			{
				'title': 'Nouvel audit',
				'camera': self.camera.id,
				'alert': self.alert.id,
				'notes': 'Reouverture legitime',
			},
			format='json'
		)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Audit.objects.count(), 2)

	def test_can_upload_capture_to_audit(self):
		audit = Audit.objects.create(
			title='Audit avec capture',
			camera=self.camera,
			alert=self.alert,
			created_by=self.user,
			status='en_cours',
		)

		image = SimpleUploadedFile(
			'capture.jpg',
			b'filecontent',
			content_type='image/jpeg',
		)

		response = self.client.post(
			reverse('audit_captures', kwargs={'audit_id': audit.id}),
			{
				'image': image,
				'description': 'Preuve terrain',
			},
			format='multipart'
		)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(AuditCapture.objects.filter(audit=audit).count(), 1)
		self.assertEqual(response.data['description'], 'Preuve terrain')
