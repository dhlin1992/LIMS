from django.contrib import admin
from .models import Patient
from .models import Batch
from .models import MachineIds
from .models import EmailAccounts

# Register your models here.
admin.site.register(Patient)
admin.site.register(Batch)
admin.site.register(MachineIds)
admin.site.register(EmailAccounts)