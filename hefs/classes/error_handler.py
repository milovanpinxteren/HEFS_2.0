from hefs.models import ErrorLogDataGerijptebieren
from datetime import datetime


class ErrorHandler():
    def log_error(self, message):
        ErrorLogDataGerijptebieren.objects.create(error_message=message, timestamp=datetime.now())
        print(message)