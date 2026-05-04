from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from Apps.Cameras.models import Camera
from Apps.alertes.models import Alert
from .gemini_service import GeminiRateLimitError, process_next_pending_gemini_analysis, register_non_compliance, sync_non_compliance_states
from .models import DetectionLog, GeminiContextAnalysis, NonComplianceState


User = get_user_model()


class GeminiQueueTests(APITestCase):
	def setUp(self):
		self.camera = Camera.objects.create(name='Cam 01', location='Zone A', status='active', is_active=True)
		self.alert = Alert.objects.create(camera=self.camera, epi_missing=['hardhat'], criticity='elevee')

	def test_persistent_non_compliance_creates_queued_gemini_analysis_for_same_person(self):
		first_log = DetectionLog.objects.create(
			camera=self.camera,
			detections_json=[
				{'class': 'person', 'status': 'missing_epi', 'bbox': [0, 0, 100, 200]},
				{'class': 'hardhat', 'status': 'missing_epi', 'bbox': [0, 0, 100, 200]},
			],
			stats_json={'missing_epi': ['hardhat'], 'compliance': False},
			is_compliant=False,
			processing_time=0.1,
		)
		state, analysis = register_non_compliance(
			camera=self.camera,
			detection_log=first_log,
			missing_epi=['hardhat'],
			alert=self.alert,
			person_bbox=[0, 0, 100, 200],
		)

		self.assertIsNotNone(state)
		self.assertIsNone(analysis)

		state.first_detected_at = timezone.now() - timedelta(minutes=5, seconds=5)
		state.save(update_fields=['first_detected_at'])

		second_log = DetectionLog.objects.create(
			camera=self.camera,
			detections_json=[
				{'class': 'person', 'status': 'missing_epi', 'bbox': [4, 0, 104, 200]},
				{'class': 'hardhat', 'status': 'missing_epi', 'bbox': [4, 0, 104, 200]},
			],
			stats_json={'missing_epi': ['hardhat'], 'compliance': False},
			is_compliant=False,
			processing_time=0.1,
		)
		state, analysis = register_non_compliance(
			camera=self.camera,
			detection_log=second_log,
			missing_epi=['hardhat'],
			alert=self.alert,
			person_bbox=[4, 0, 104, 200],
		)

		self.assertTrue(state.queued_for_llm)
		self.assertIsNotNone(analysis)
		self.assertEqual(analysis.status, 'queued')
		self.assertEqual(GeminiContextAnalysis.objects.count(), 1)
		self.assertEqual(NonComplianceState.objects.count(), 1)

	def test_different_person_does_not_inherit_previous_person_timer(self):
		first_log = DetectionLog.objects.create(
			camera=self.camera,
			detections_json=[],
			stats_json={'missing_epi': ['hardhat'], 'compliance': False},
			is_compliant=False,
			processing_time=0.1,
		)
		state, _ = register_non_compliance(
			camera=self.camera,
			detection_log=first_log,
			missing_epi=['hardhat'],
			alert=self.alert,
			person_bbox=[0, 0, 100, 200],
		)

		state.first_detected_at = timezone.now() - timedelta(minutes=6)
		state.save(update_fields=['first_detected_at'])

		second_log = DetectionLog.objects.create(
			camera=self.camera,
			detections_json=[],
			stats_json={'missing_epi': ['hardhat'], 'compliance': False},
			is_compliant=False,
			processing_time=0.1,
		)
		second_state, analysis = register_non_compliance(
			camera=self.camera,
			detection_log=second_log,
			missing_epi=['hardhat'],
			alert=self.alert,
			person_bbox=[300, 0, 400, 200],
		)

		self.assertNotEqual(state.person_key, second_state.person_key)
		self.assertIsNone(analysis)
		self.assertEqual(NonComplianceState.objects.filter(is_active=True).count(), 2)

	def test_sync_non_compliance_resolves_person_missing_from_current_frame(self):
		first_log = DetectionLog.objects.create(
			camera=self.camera,
			detections_json=[],
			stats_json={'missing_epi': ['hardhat'], 'compliance': False},
			is_compliant=False,
			processing_time=0.1,
		)
		state, _ = register_non_compliance(
			camera=self.camera,
			detection_log=first_log,
			missing_epi=['hardhat'],
			alert=self.alert,
			person_bbox=[0, 0, 100, 200],
		)

		compliant_log = DetectionLog.objects.create(
			camera=self.camera,
			detections_json=[],
			stats_json={'missing_epi': [], 'compliance': True},
			is_compliant=True,
			processing_time=0.1,
		)
		sync_non_compliance_states(
			camera=self.camera,
			detection_log=compliant_log,
			person_observations=[],
		)

		state.refresh_from_db()
		self.assertFalse(state.is_active)
		self.assertIsNotNone(state.resolved_at)

	@patch('Apps.detection.gemini_service.analyze_gemini_context')
	def test_rate_limited_gemini_analysis_is_requeued(self, mock_analyze):
		mock_analyze.side_effect = GeminiRateLimitError(
			'429 quota exceeded. Please retry in 2.4s.',
			retry_after_seconds=2,
		)

		log = DetectionLog.objects.create(
			camera=self.camera,
			detections_json=[],
			stats_json={'missing_epi': ['hardhat'], 'compliance': False},
			is_compliant=False,
			processing_time=0.1,
		)
		state = NonComplianceState.objects.create(
			camera=self.camera,
			person_key='tracked-person-2',
			signature='hardhat',
			missing_epi=['hardhat'],
			last_known_bbox=[0, 0, 100, 200],
			first_detected_at=timezone.now() - timedelta(minutes=6),
			last_detected_at=timezone.now(),
			last_seen_log=log,
			queued_for_llm=True,
		)
		analysis = GeminiContextAnalysis.objects.create(
			camera=self.camera,
			detection_log=log,
			non_compliance_state=state,
			missing_epi=['hardhat'],
			request_reason='Non-conformité persistante >= 5 minutes',
		)

		processed_analysis, outcome = process_next_pending_gemini_analysis()

		analysis.refresh_from_db()
		self.assertEqual(outcome, 'rate_limited')
		self.assertEqual(processed_analysis.id, analysis.id)
		self.assertEqual(analysis.status, 'queued')
		self.assertIn('429', analysis.error_message)
		self.assertIsNotNone(analysis.next_retry_at)
		self.assertIsNone(analysis.processed_at)

	def test_process_next_returns_retry_scheduled_when_only_blocked_items_exist(self):
		log = DetectionLog.objects.create(
			camera=self.camera,
			detections_json=[],
			stats_json={'missing_epi': ['hardhat'], 'compliance': False},
			is_compliant=False,
			processing_time=0.1,
		)
		state = NonComplianceState.objects.create(
			camera=self.camera,
			person_key='tracked-person-3',
			signature='hardhat',
			missing_epi=['hardhat'],
			last_known_bbox=[0, 0, 100, 200],
			first_detected_at=timezone.now() - timedelta(minutes=6),
			last_detected_at=timezone.now(),
			last_seen_log=log,
			queued_for_llm=True,
		)
		analysis = GeminiContextAnalysis.objects.create(
			camera=self.camera,
			detection_log=log,
			non_compliance_state=state,
			missing_epi=['hardhat'],
			request_reason='Non-conformité persistante >= 5 minutes',
			status='queued',
			next_retry_at=timezone.now() + timedelta(seconds=15),
		)

		selected_analysis, outcome = process_next_pending_gemini_analysis()

		self.assertEqual(outcome, 'retry_scheduled')
		self.assertEqual(selected_analysis.id, analysis.id)


class GeminiAnalysisViewPermissionsTests(APITestCase):
	def setUp(self):
		self.client = APIClient()
		self.camera = Camera.objects.create(name='Cam 02', location='Zone B', status='active', is_active=True)
		self.admin_user = User.objects.create_user(
			email='admin@example.com',
			password='Password123',
			first_name='Admin',
			last_name='User',
			role='admin',
		)
		self.operator_user = User.objects.create_user(
			email='operator@example.com',
			password='Password123',
			first_name='Operator',
			last_name='User',
			role='operateur',
		)
		log = DetectionLog.objects.create(
			camera=self.camera,
			detections_json=[],
			stats_json={'missing_epi': ['hardhat'], 'compliance': False},
			is_compliant=False,
			processing_time=0.1,
		)
		state = NonComplianceState.objects.create(
			camera=self.camera,
			person_key='tracked-person-1',
			signature='hardhat',
			missing_epi=['hardhat'],
			last_known_bbox=[0, 0, 100, 200],
			first_detected_at=timezone.now() - timedelta(minutes=6),
			last_detected_at=timezone.now(),
			last_seen_log=log,
			queued_for_llm=True,
		)
		GeminiContextAnalysis.objects.create(
			camera=self.camera,
			detection_log=log,
			non_compliance_state=state,
			missing_epi=['hardhat'],
			request_reason='Non-conformité persistante >= 5 minutes',
		)

	def test_admin_can_list_gemini_analyses(self):
		self.client.force_authenticate(user=self.admin_user)
		response = self.client.get(reverse('gemini_context_analysis_list'))
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_operator_cannot_list_gemini_analyses(self):
		self.client.force_authenticate(user=self.operator_user)
		response = self.client.get(reverse('gemini_context_analysis_list'))
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
