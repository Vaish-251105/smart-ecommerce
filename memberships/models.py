from django.db import models

from users.models import AppUser

class MembershipPlan(models.Model):
    MEMBERSHIP_CHOICES = [
        ('educational','Educational'),
        ('silver','Silver'),
        ('gold','Gold'),
    ]

    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    membership_type = models.CharField(max_length=20, choices=MEMBERSHIP_CHOICES)
    is_student = models.BooleanField(default=False)
    student_roll_no = models.CharField(max_length=30, null=True, blank=True)
    student_verified = models.BooleanField(default=False)
    semester = models.CharField(max_length=10)
    membership_start_date = models.DateField()
    membership_end_date = models.DateField()
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2)
    priority_level = models.IntegerField()
    status = models.CharField(max_length=15)
