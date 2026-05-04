import json
import re
from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone

from .models import DetectionLog, GeminiContextAnalysis, NonComplianceState


PERSON_TRACK_IOU_THRESHOLD = 0.5
DEFAULT_GEMINI_RETRY_SECONDS = 60


class GeminiRateLimitError(RuntimeError):
    def __init__(self, message: str, retry_after_seconds: int | None = None):
        super().__init__(message)
        self.retry_after_seconds = retry_after_seconds


def _build_retry_datetime(retry_after_seconds: int | None):
    wait_seconds = retry_after_seconds or DEFAULT_GEMINI_RETRY_SECONDS
    return timezone.now() + timezone.timedelta(seconds=wait_seconds)


def build_missing_signature(missing_epi: list[str]) -> str:
    return '|'.join(sorted({item for item in missing_epi if item}))


def get_required_epi(camera, fallback_missing_epi: list[str]) -> list[str]:
    if not camera:
        return fallback_missing_epi

    epis = []
    for rule in camera.hse_rules.filter(is_active=True):
        for item in rule.epi_criticites:
            epi = item.get('epi') if isinstance(item, dict) else item
            if epi:
                epis.append(epi)

    return sorted({epi for epi in epis}) or fallback_missing_epi


def build_gemini_prompt(analysis: GeminiContextAnalysis) -> str:
    required_epi = get_required_epi(analysis.camera, analysis.missing_epi)
    zone = analysis.camera.location if analysis.camera and analysis.camera.location else 'zone non renseignée'

    return f"""Tu es un système expert en sécurité industrielle et conformité EPI.

Contexte :
- Caméra : {analysis.camera.name if analysis.camera else 'Inconnue'}
- Zone : {zone}
- Non-conformité persistante détectée pendant au moins {settings.GEMINI_PERSISTENCE_MINUTES} minutes
- EPI manquants détectés par YOLO : {analysis.missing_epi}
- EPI requis pour la zone : {required_epi}
- Motif de soumission : {analysis.request_reason or 'non-conformité persistante'}

Analyse l'image et réponds UNIQUEMENT en JSON valide :
{{
  "incident": true,
  "confirmed_epi": ["liste des EPI visibles confirmés"],
  "missing_epi": ["liste des EPI manquants confirmés"],
  "severity": "low|medium|high",
  "confidence": 0.0,
  "explanation": "explication courte en français",
  "action": "ALERT|MONITOR|OK"
}}"""


def _parse_json_response(raw_text: str) -> dict:
    cleaned = raw_text.strip()
    if '```json' in cleaned:
        cleaned = cleaned.split('```json', 1)[1].split('```', 1)[0].strip()
    elif '```' in cleaned:
        cleaned = cleaned.split('```', 1)[1].split('```', 1)[0].strip()
    return json.loads(cleaned)


def _extract_retry_after_seconds(message: str) -> int | None:
    match = re.search(r'retry in\s+([0-9]+(?:\.[0-9]+)?)s', message, flags=re.IGNORECASE)
    if not match:
        return None

    try:
        return max(1, round(float(match.group(1))))
    except ValueError:
        return None


def _is_rate_limit_error(message: str) -> bool:
    normalized = message.lower()
    return '429' in normalized or 'quota exceeded' in normalized or 'rate limit' in normalized


def _get_analysis_image_field(analysis: GeminiContextAnalysis):
    if analysis.image:
        return analysis.image
    if analysis.alert and analysis.alert.image:
        return analysis.alert.image
    return None


def _snapshot_image_if_needed(analysis: GeminiContextAnalysis, image_file) -> None:
    if analysis.image or not image_file:
        return

    try:
        image_file.seek(0)
    except Exception:
        pass

    content = image_file.read()
    if not content:
        return

    file_name = Path(getattr(image_file, 'name', 'gemini-context.jpg')).name
    analysis.image.save(
        f"gemini-{timezone.now().strftime('%Y%m%d%H%M%S')}-{file_name}",
        ContentFile(content),
        save=False,
    )


def _normalize_bbox(bbox) -> list[int] | None:
    if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
        return None

    try:
        normalized = [int(value) for value in bbox]
    except (TypeError, ValueError):
        return None

    if normalized[2] <= normalized[0] or normalized[3] <= normalized[1]:
        return None

    return normalized


def _bbox_key(bbox: list[int]) -> str:
    return '|'.join(str(value) for value in bbox)


def _iou(box1: list[int], box2: list[int]) -> float:
    inter_x_min = max(box1[0], box2[0])
    inter_y_min = max(box1[1], box2[1])
    inter_x_max = min(box1[2], box2[2])
    inter_y_max = min(box1[3], box2[3])

    if inter_x_max <= inter_x_min or inter_y_max <= inter_y_min:
        return 0.0

    inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union_area = box1_area + box2_area - inter_area
    return inter_area / union_area if union_area > 0 else 0.0


def extract_non_compliant_person_observations(detections: list[dict], allowed_missing_epi: list[str] | None = None) -> list[dict]:
    allowed = set(allowed_missing_epi or [])
    missing_by_bbox: dict[str, dict] = {}

    for detection in detections:
        if detection.get('status') != 'missing_epi':
            continue

        bbox = _normalize_bbox(detection.get('bbox'))
        epi_class = detection.get('class')
        if not bbox or not epi_class or epi_class == 'person':
            continue
        if allowed and epi_class not in allowed:
            continue

        key = _bbox_key(bbox)
        bucket = missing_by_bbox.setdefault(key, {'bbox': bbox, 'missing_epi': []})
        if epi_class not in bucket['missing_epi']:
            bucket['missing_epi'].append(epi_class)

    observations = []
    for detection in detections:
        if detection.get('class') != 'person' or detection.get('status') != 'missing_epi':
            continue

        bbox = _normalize_bbox(detection.get('bbox'))
        if not bbox:
            continue

        entry = missing_by_bbox.get(_bbox_key(bbox))
        if entry and entry['missing_epi']:
            observations.append({
                'bbox': bbox,
                'missing_epi': sorted(entry['missing_epi']),
            })

    return observations


def _resolve_states(states: list[NonComplianceState], resolved_at) -> None:
    state_ids = [state.id for state in states if state.id]
    if state_ids:
        NonComplianceState.objects.filter(id__in=state_ids, is_active=True).update(
            is_active=False,
            resolved_at=resolved_at,
        )


def _match_active_state(active_states: list[NonComplianceState], person_bbox: list[int], matched_ids: set[int]) -> NonComplianceState | None:
    best_state = None
    best_iou = 0.0

    for state in active_states:
        if state.id in matched_ids:
            continue

        state_bbox = _normalize_bbox(state.last_known_bbox)
        if not state_bbox:
            continue

        overlap = _iou(state_bbox, person_bbox)
        if overlap >= PERSON_TRACK_IOU_THRESHOLD and overlap > best_iou:
            best_state = state
            best_iou = overlap

    return best_state


def _queue_analysis_if_needed(state: NonComplianceState, camera, detection_log: DetectionLog, missing_epi: list[str], alert=None, image_file=None):
    queued_analysis = None
    elapsed_seconds = (state.last_detected_at - state.first_detected_at).total_seconds()
    if elapsed_seconds >= settings.GEMINI_PERSISTENCE_MINUTES * 60 and not state.queued_for_llm:
        queued_analysis = GeminiContextAnalysis.objects.create(
            camera=camera,
            alert=alert,
            detection_log=detection_log,
            non_compliance_state=state,
            missing_epi=missing_epi,
            request_reason=f"Non-conformité persistante >= {settings.GEMINI_PERSISTENCE_MINUTES} minutes",
        )
        _snapshot_image_if_needed(queued_analysis, image_file)
        queued_analysis.save()
        state.queued_for_llm = True
        state.save(update_fields=['queued_for_llm', 'updated_at'])

    return queued_analysis


@transaction.atomic
def sync_non_compliance_states(
    camera,
    detection_log: DetectionLog,
    person_observations: list[dict],
    alert=None,
    image_file=None,
    resolve_absent_states: bool = True,
):
    if not camera:
        return [], []

    now = detection_log.timestamp or timezone.now()
    active_states = list(
        NonComplianceState.objects.select_for_update().filter(camera=camera, is_active=True).order_by('first_detected_at')
    )

    matched_state_ids: set[int] = set()
    touched_states = []
    queued_analyses = []

    for observation in person_observations:
        person_bbox = _normalize_bbox(observation.get('bbox'))
        missing_epi = sorted({item for item in observation.get('missing_epi', []) if item})
        if not person_bbox or not missing_epi:
            continue

        signature = build_missing_signature(missing_epi)
        state = _match_active_state(active_states, person_bbox, matched_state_ids)

        if state:
            matched_state_ids.add(state.id)
            state.signature = signature
            state.missing_epi = missing_epi
            state.last_known_bbox = person_bbox
            state.last_detected_at = now
            state.last_seen_log = detection_log
            state.is_active = True
            state.resolved_at = None
            state.save(update_fields=[
                'signature',
                'missing_epi',
                'last_known_bbox',
                'last_detected_at',
                'last_seen_log',
                'is_active',
                'resolved_at',
                'updated_at',
            ])
        else:
            state = NonComplianceState.objects.create(
                camera=camera,
                person_key=uuid4().hex,
                signature=signature,
                missing_epi=missing_epi,
                last_known_bbox=person_bbox,
                first_detected_at=now,
                last_detected_at=now,
                last_seen_log=detection_log,
            )
            active_states.append(state)
            matched_state_ids.add(state.id)

        queued_analysis = _queue_analysis_if_needed(
            state=state,
            camera=camera,
            detection_log=detection_log,
            missing_epi=missing_epi,
            alert=alert,
            image_file=image_file,
        )
        if queued_analysis:
            queued_analyses.append(queued_analysis)
        touched_states.append(state)

    if resolve_absent_states:
        states_to_resolve = [state for state in active_states if state.id not in matched_state_ids]
        _resolve_states(states_to_resolve, now)

    return touched_states, queued_analyses


@transaction.atomic
def register_non_compliance(camera, detection_log: DetectionLog, missing_epi: list[str], alert=None, image_file=None, person_bbox=None):
    if not camera or not missing_epi or not person_bbox:
        return None, None

    states, queued_analyses = sync_non_compliance_states(
        camera=camera,
        detection_log=detection_log,
        person_observations=[{'bbox': person_bbox, 'missing_epi': missing_epi}],
        alert=alert,
        image_file=image_file,
        resolve_absent_states=False,
    )
    return (states[0] if states else None), (queued_analyses[0] if queued_analyses else None)


def get_daily_processed_count() -> int:
    today = timezone.localdate()
    return GeminiContextAnalysis.objects.filter(started_at__date=today).count()


def analyze_gemini_context(analysis: GeminiContextAnalysis) -> dict:
    if not settings.GEMINI_API_KEY:
        raise RuntimeError('GEMINI_API_KEY is not configured.')

    try:
        import google.generativeai as genai
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError('google-generativeai or Pillow is not installed.') from exc

    image_field = _get_analysis_image_field(analysis)
    if not image_field:
        raise RuntimeError('No image is available for this Gemini analysis.')

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(settings.GEMINI_MODEL)

    image_field.open('rb')
    try:
        pil_image = Image.open(image_field)
        prompt = build_gemini_prompt(analysis)
        try:
            response = model.generate_content([prompt, pil_image])
        except Exception as exc:
            message = str(exc)
            if _is_rate_limit_error(message):
                raise GeminiRateLimitError(message, retry_after_seconds=_extract_retry_after_seconds(message)) from exc
            raise
    finally:
        image_field.close()

    raw_text = getattr(response, 'text', '').strip()
    result = _parse_json_response(raw_text)

    return {
        'prompt': prompt,
        'response_text': raw_text,
        'result_json': result,
        'severity': result.get('severity') or 'medium',
        'action': result.get('action') or 'MONITOR',
        'explanation': result.get('explanation') or '',
        'llm_confidence': result.get('confidence'),
    }


@transaction.atomic
def process_next_pending_gemini_analysis():
    if get_daily_processed_count() >= settings.GEMINI_DAILY_LIMIT:
        return None, 'daily_limit_reached'

    now = timezone.now()
    queue_queryset = GeminiContextAnalysis.objects.select_related('camera', 'alert', 'detection_log').filter(status='queued')
    analysis = queue_queryset.filter(next_retry_at__isnull=True).first() or queue_queryset.filter(next_retry_at__lte=now).first()
    if not analysis:
        blocked_analysis = queue_queryset.filter(next_retry_at__gt=now).order_by('next_retry_at').first()
        if blocked_analysis:
            return blocked_analysis, 'retry_scheduled'
        return None, 'empty_queue'

    analysis.status = 'processing'
    analysis.started_at = timezone.now()
    analysis.next_retry_at = None
    analysis.error_message = ''
    analysis.save(update_fields=['status', 'started_at', 'next_retry_at', 'error_message', 'updated_at'])

    try:
        payload = analyze_gemini_context(analysis)
        analysis.status = 'completed'
        analysis.prompt = payload['prompt']
        analysis.response_text = payload['response_text']
        analysis.result_json = payload['result_json']
        analysis.severity = payload['severity']
        analysis.action = payload['action']
        analysis.explanation = payload['explanation']
        analysis.llm_confidence = payload['llm_confidence']
        analysis.processed_at = timezone.now()
        analysis.next_retry_at = None
        analysis.save()
        return analysis, 'processed'
    except GeminiRateLimitError as exc:
        analysis.status = 'queued'
        analysis.error_message = str(exc)
        analysis.next_retry_at = _build_retry_datetime(exc.retry_after_seconds)
        analysis.save(update_fields=['status', 'error_message', 'next_retry_at', 'updated_at'])
        return analysis, 'rate_limited'
    except Exception as exc:
        analysis.status = 'failed'
        analysis.error_message = str(exc)
        analysis.next_retry_at = None
        analysis.processed_at = timezone.now()
        analysis.save(update_fields=['status', 'error_message', 'next_retry_at', 'processed_at', 'updated_at'])
        return analysis, 'failed'