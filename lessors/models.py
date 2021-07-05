from django.db import models

# Create your models here.

class Lessor(models.Model):
    # Fields
    name = models.CharField(max_length=20, help_text='Enter field documentation')
    ...

    # Metadata
    class Meta:
        ordering = ['-name']

    # Methods
    def get_absolute_url(self):
        """Returns the url to access a particular instance of MyModelName."""
        return reverse('model-detail-view', args=[str(self.id)])
  
    def __str__(self):
        """String for representing the MyModelName object (in Admin site etc.)."""
        return self.name
