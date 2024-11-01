from django.db import models

# Create your models here.

class CategoryMaster(models.Model):
    Order = models.IntegerField()
    Category =  models.CharField(max_length=100)

    def __str__(self):
        return f"{self.Order} {self.Category}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["Category"],
                name="CategoryMasterFilter_unique"
            ),
        ]

class Ivents(models.Model):
    Category =  models.ForeignKey(CategoryMaster, on_delete=models.CASCADE)
    IventName =  models.CharField(max_length=100)
    Disabled = models.DateTimeField()
    URL = models.CharField(max_length=2048)

    def __str__(self):
        return f"{self.IventName}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["IventName"],
                name="IventsFilter_unique"
            ),
        ]
