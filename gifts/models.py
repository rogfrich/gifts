from django.db import models
from django.contrib.auth.models import User

class Gift(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gifts_user')
    title = models.CharField(max_length=100)
    detail = models.TextField()
    link = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    claimed = models.BooleanField(default=False)
    claimed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gifts_claimed_by', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Gifts'