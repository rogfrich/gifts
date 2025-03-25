from django.db import models
from django.contrib.auth.models import User

class Wish(models.Model):  # Renamed from Gift to Wish
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishes_user')  # Updated related_name
    title = models.CharField(max_length=100)
    detail = models.TextField()
    link = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    claimed = models.BooleanField(default=False)
    claimed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishes_claimed_by', null=True, blank=True)  # Updated related_name
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Wishes'  # Updated verbose name