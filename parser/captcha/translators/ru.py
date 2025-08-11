import string

from .base import BaseInstructionsTranslator
from .exceptions import CaptchaInstructionTranslationError


_TRANSLATIONS = {
    "автомобил": "car",
    "велосипед": "bicycle",
    "лодк": "boat",
    "мост": "bridge",
    "автобус": "bus",
    "дымоход": "chimney",
    "зебр": "crosswalk",
    "гидрант": "hydrant",
    "мотоцикл": "motorcycle",
    "гор": "mountain",
    "пальм": "palms tree",
    "светофор": "traffic light",
    "трактор": "tractor",
    "такси": "taxi",
    "лестниц": "stair",
    "парков": "parking meter"
}


class RUInstructionsTranslator(BaseInstructionsTranslator):
    @property
    def translated(self):
        if set(self._instruction.lower()) & set(string.ascii_lowercase):
            return self._instruction

        for key, value in _TRANSLATIONS.items():
            if key in self._instruction:
                return value

        raise CaptchaInstructionTranslationError(
            "Cannot translate captcha instruction from russian!"
        )
