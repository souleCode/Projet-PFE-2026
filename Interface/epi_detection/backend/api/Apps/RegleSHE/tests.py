from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from Apps.Users.models import User
from .models import HSERule


class HSERulePermissionsTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.admin = User.objects.create_user(
			email='admin@example.com',
			password='password123',
			first_name='Admin',
			last_name='User',
			role='admin',
		)
		self.operator = User.objects.create_user(
			email='operator@example.com',
			password='password123',
			first_name='Operator',
			last_name='User',
			role='operateur',
		)
		self.rule = HSERule.objects.create(
			name='Casque obligatoire',
			epi_criticites=[{'epi': 'hardhat', 'criticite': 'elevee'}],
		)
		self.list_url = '/api/hse-rules/'
		self.detail_url = f'/api/hse-rules/{self.rule.pk}/'

	def test_authenticated_operator_can_list_rules(self):
		self.client.force_authenticate(user=self.operator)

		response = self.client.get(self.list_url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_operator_cannot_create_rule(self):
		self.client.force_authenticate(user=self.operator)

		response = self.client.post(
			self.list_url,
			{
				'name': 'Gilet obligatoire',
				'epi_criticites': [{'epi': 'safety_vest', 'criticite': 'moyenne'}],
				'is_active': True,
			},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_admin_can_create_rule(self):
		self.client.force_authenticate(user=self.admin)

		response = self.client.post(
			self.list_url,
			{
				'name': 'Gilet obligatoire',
				'epi_criticites': [{'epi': 'safety_vest', 'criticite': 'moyenne'}],
				'is_active': True,
			},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

	def test_operator_cannot_update_rule(self):
		self.client.force_authenticate(user=self.operator)

		response = self.client.patch(
			self.detail_url,
			{'name': 'Nom modifie'},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_admin_can_delete_rule(self):
		self.client.force_authenticate(user=self.admin)

		response = self.client.delete(self.detail_url)

		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
