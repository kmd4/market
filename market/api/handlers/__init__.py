from .citizen import CitizenView
from .citizen_birthdays import CitizenBirthdaysView
from .citizens import CitizensView
from .imports import ImportsView


HANDLERS = (
    CitizenBirthdaysView, CitizensView, CitizenView, ImportsView,
)