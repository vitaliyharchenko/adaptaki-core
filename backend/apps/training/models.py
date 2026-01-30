"""
Infrastructure layer: Django ORM models live in apps.training.infrastructure.models.

This module re-exports them so Django can auto-discover models via apps.training.
"""

from .infrastructure.models import TaskAttempt, Test, TestAttempt, TestItem

__all__ = ["Test", "TestItem", "TestAttempt", "TaskAttempt"]

