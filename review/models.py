from typing import Any
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings

# Create your models here.

class ReviewedProductManager(models.Manager):
    def get_reviews_for(self, obj_type, obj_id):
        content_type = ContentType.objects.get_for_model(obj_type)

        return ReviewedProduct.objects\
            .select_related(Review)\
            .filter(
                content_type=content_type, object_id=obj_id
            )


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    summary = models.CharField(max_length=255)
    details = models.TextField(null=True)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    date = models.DateField(auto_now_add=True)


class ReviewedItem(models.Model):
    objects = ReviewedProductManager()
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveSmallIntegerField()
    content_object = GenericForeignKey()
    