from django.db import models

# Create your models here.

class ConditionFilter(models.Model):
    Order =  models.IntegerField()
    DisplayName =  models.CharField(max_length=100)

    def __str__(self):
        return f"{self.Order} {self.DisplayName}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["Order"],
                name="ConditionFilter_unique"
            ),
        ]

class Condition(models.Model):
    Order =  models.IntegerField()
    DisplayName =  models.CharField(max_length=100)
    Query =  models.CharField(max_length=100)
    FilterID =  models.ForeignKey(ConditionFilter, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.FilterID} {self.Order} {self.DisplayName}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["Order", "FilterID"],
                name="Condition_unique"
            ),
        ]

class EffectFilter(models.Model):
    Order =  models.IntegerField()
    DisplayName =  models.CharField(max_length=100)

    def __str__(self):
        return f"{self.Order} {self.DisplayName}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["Order"],
                name="EffectFilter_unique"
            ),
        ]

class Effect(models.Model):
    Order =  models.IntegerField()
    DisplayName =  models.CharField(max_length=100)
    Query =  models.CharField(max_length=100)
    FilterID =  models.ForeignKey(EffectFilter, on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.FilterID} {self.Order} {self.DisplayName}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["Order", "FilterID"],
                name="Effect_unique"
            ),
        ]

class Part(models.Model):
    Order =  models.IntegerField()
    DisplayName =  models.CharField(max_length=100)
    Query =  models.CharField(max_length=100)

    def __str__(self):
        return f"{self.Order} {self.DisplayName}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["Order"],
                name="Part_unique"
            ),
        ]

class WordTag(models.Model):
    Order =  models.IntegerField()
    DisplayName =  models.CharField(max_length=100)

    def __str__(self):
        return f"{self.Order} {self.DisplayName}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["Order"],
                name="WordTag_unique"
            ),
        ]