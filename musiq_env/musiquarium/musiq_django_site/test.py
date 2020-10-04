import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR.__str__(), 'static'),
)
STATIC_ROOT = os.path.join(BASE_DIR.__str__(), 'staticfiles')

print(STATICFILES_DIRS)
