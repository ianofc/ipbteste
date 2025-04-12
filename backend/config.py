import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uma_chave_secreta'
    BIBLE_API_URL = "https://bible-api.com/data"  # URL base da API da Bíblia
    BIBLE_VERSION = "almeida"  # Versão desejada
    CALENDAR_API_URL = "https://calendarific.com/api/v2/holidays"
    CALENDARIFIC_API_KEY = os.environ.get('CALENDARIFIC_API_KEY')  # Defina sua chave de API aqui
    CHURCH_ADDRESS = "Rua Coronel Antônio Afonso, 38, Palmeiras-BA"