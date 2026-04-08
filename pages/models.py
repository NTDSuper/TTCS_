# models.py
from django.db import models
from django.conf import settings # Dùng để tham chiếu đến User model (nếu cần cho DiagnosisRecord)
from django.utils import timezone
import os.path # Cần import os.path cho phương thức __str__ của DiagnosisHistory


class DiagnosisRecord(models.Model):
   
    image = models.ImageField(upload_to='diagnosis_images/%Y/%m/%d/')
    
    result = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        
         return f"Diagnosis at {self.timestamp.strftime('%Y-%m-%d %H:%M')}: {self.result}" 
    class Meta:
        
        ordering = ['-timestamp']

class DiagnosisHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    
    file = models.FileField(upload_to='history_files/')
    result = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        
        file_name = os.path.basename(self.file.name) if self.file and hasattr(self.file, 'name') and self.file.name else "No file"
        return f"{self.result} - {file_name} - {self.date.strftime('%Y-%m-%d %H:%M')}"

