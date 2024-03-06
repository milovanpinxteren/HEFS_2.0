from hefs.models import ErrorLogDataGerijptebieren
from datetime import datetime
import warnings

class ErrorHandler():
    def log_error(self, message):
        warnings.filterwarnings("ignore")
        ErrorLogDataGerijptebieren.objects.create(error_message=message, timestamp=datetime.now())
        print(message)