from .models import Alert


def compute_criticity(missing_epi: list) -> str:
    """
    Calcule la criticité en fonction des EPI manquants.
    - hardhat seul manquant  → élevée  (risque tête)
    - vest seul manquant     → moyenne (visibilité)
    - plusieurs manquants    → élevée
    - aucun (conformité OK)  → faible
    """
    if not missing_epi:
        return 'faible'
    if 'hardhat' in missing_epi or len(missing_epi) >= 2:
        return 'elevee'
    return 'moyenne'


def create_alert_if_needed(camera, missing_epi, image_file=None, detection_log=None):
    """
    Crée une alerte uniquement si des EPI sont manquants.
    Évite les doublons : pas d'alerte si une alerte 'nouveau' ou 'en_cours'
    existe déjà pour cette caméra avec les mêmes EPI manquants.
    """
    if not missing_epi:
        return None

    # Anti-doublon : alerte ouverte récente sur cette caméra ?
    existing = Alert.objects.filter(
        camera   = camera,
        status__in = ['nouveau', 'en_cours'],
        epi_missing = missing_epi,
    ).first()

    if existing:
        return existing   # On retourne l'alerte existante sans en créer une nouvelle

    criticity = compute_criticity(missing_epi)

    alert = Alert.objects.create(
        camera        = camera,
        epi_missing   = missing_epi,
        criticity     = criticity,
        image         = image_file,
        detection_log = detection_log,
    )
    return alert