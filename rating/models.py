import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from django.contrib.contenttypes import generic

from rating.managers import *

class RatedItem(models.Model):
  """
  Rate info for an object.

  """
  rating_average = models.DecimalField(max_digits=7, decimal_places=2)
  rating_count = models.PositiveIntegerField()
  date_last_rated = models.DateTimeField(editable=False, null=True)
  content_type = models.ForeignKey(ContentType)
  object_id = models.PositiveIntegerField()
  object = generic.GenericForeignKey('content_type', 'object_id')
  objects = RatedItemManager()

  class Meta:
    unique_together = (('content_type', 'object_id'),)

  def __unicode__(self):
      return u'Rating for %s' % self.object

  def add_or_update_rating(self, value, user):
    now = datetime.datetime.now()
    rating, created = Rating.objects.get_or_create(
      user = user,
      rated_object = self,
      defaults = {
        'date': now,
        'rating': value,
      }
    )
    if not created:
      rating.rating = value
      rating.date = now
      rating.save()
    self.rating_count = self.ratings.count()
    self.rating_average = str(Rating.objects.rating_average(self.object))
    self.date_last_rated = now
    self.save()
    return self

  def get_average(self):
    return '%.1f' % self.rating_average

  def save(self, *args, **kwargs):
    if not self.id:
      self.rating_count = 0
      self.rating_average = 0
    super(RatedItem, self).save(*args, **kwargs)


class Rating(models.Model):
  """
  Rating detail.
  """
  rated_object = models.ForeignKey('RatedItem', related_name='ratings')
  user = models.ForeignKey(User, null=True, blank=True, related_name='ratings')
  rating = models.PositiveSmallIntegerField()
  date = models.DateTimeField(_('rated on'), editable=False)

  objects = RatingManager()

  def __unicode__(self):
    return u"%s: %s by %s" % (self.rated_object, self.rating, self.user)
    
  def save(self, *args, **kwargs):
    if not self.id:
      self.date = datetime.datetime.now()
    super(Rating, self).save(*args, **kwargs)
