"""
Utilitaires pour la gestion centralisée des dates et fuseaux horaires

Règles:
- Toutes les dates stockées en MongoDB sont en UTC
- Les conversions timezone sont gérées côté frontend
- Utiliser toujours timezone-aware datetime objects
"""

from datetime import datetime, timezone
from typing import Optional


def now_utc() -> datetime:
    """
    Retourne la date/heure actuelle en UTC (timezone-aware)
    
    Returns:
        datetime: Date/heure actuelle en UTC
    """
    return datetime.now(timezone.utc)


def parse_iso_date(date_string: str) -> datetime:
    """
    Parser une date ISO en datetime UTC
    
    Args:
        date_string: Date au format ISO (ex: "2025-12-25T09:00:00Z" ou "2025-12-25T09:00:00+01:00")
        
    Returns:
        datetime: Date parsée en UTC
    """
    # Remplacer 'Z' par '+00:00' pour le parser correctement
    date_string = date_string.replace('Z', '+00:00')
    
    # Parser la date
    dt = datetime.fromisoformat(date_string)
    
    # Convertir en UTC si nécessaire
    if dt.tzinfo is None:
        # Si pas de timezone, assumer UTC
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        # Convertir en UTC
        dt = dt.astimezone(timezone.utc)
    
    return dt


def to_utc(dt: datetime) -> datetime:
    """
    Convertir un datetime en UTC
    
    Args:
        dt: Datetime à convertir
        
    Returns:
        datetime: Datetime en UTC
    """
    if dt.tzinfo is None:
        # Si pas de timezone, assumer UTC
        return dt.replace(tzinfo=timezone.utc)
    
    # Convertir en UTC
    return dt.astimezone(timezone.utc)


def start_of_day_utc(dt: Optional[datetime] = None) -> datetime:
    """
    Retourne le début de la journée en UTC (00:00:00)
    
    Args:
        dt: Date de référence (défaut: aujourd'hui)
        
    Returns:
        datetime: Début de journée en UTC
    """
    if dt is None:
        dt = now_utc()
    
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def format_for_frontend(dt: datetime) -> str:
    """
    Formater une date pour l'envoi au frontend (ISO format avec timezone)
    
    Args:
        dt: Datetime à formater
        
    Returns:
        str: Date au format ISO avec timezone
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt.isoformat()


def is_past(dt: datetime) -> bool:
    """
    Vérifier si une date est dans le passé
    
    Args:
        dt: Date à vérifier
        
    Returns:
        bool: True si la date est passée
    """
    return to_utc(dt) < now_utc()


def is_future(dt: datetime) -> bool:
    """
    Vérifier si une date est dans le futur
    
    Args:
        dt: Date à vérifier
        
    Returns:
        bool: True si la date est dans le futur
    """
    return to_utc(dt) > now_utc()
