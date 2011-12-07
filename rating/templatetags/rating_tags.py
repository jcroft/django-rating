from django import template
from django.contrib.contenttypes.models import ContentType
from django.template.loader import get_template
from django.core.exceptions import MultipleObjectsReturned


from rating.models import *
from rating.utils import get_target_for_object

register = template.Library()

class GetUserRatingNode(template.Node):
  def __init__(self, object_name, user, var_name):
    self.object_name, self.user, self.var_name = object_name, user, var_name

  def render(self, context):
    object = template.resolve_variable(self.object_name, context)
    user = template.resolve_variable(self.user, context)
    try:
      rating = Rating.objects.get(rated_object__object_id=object.id, rated_object__content_type=ContentType.objects.get_for_model(object), user=user)
    except Rating.DoesNotExist:
      rating = None
    except (Rating.MultipleObjectsReturned, MultipleObjectsReturned):
      # If, for some reason, there are multiple ratings for the same objects by the same person, straighten this out.
      ratings = Rating.objects.filter(rated_object__object_id=object.id, rated_object__content_type=ContentType.objects.get_for_model(object), user=user)
      for r in ratings[1:]:
        r.delete()
      rating = Rating.objects.get(rated_object__object_id=object.id, rated_object__content_type=ContentType.objects.get_for_model(object), user=user)
      
    context[self.var_name] = rating
    return ''


@register.tag('get_user_rating')
def do_get_user_rating(parser, token):
  """
  Syntax::

    {% get_user_rating for [object] by [user] as [varname] %}

  Example usage::

    {% get_user_rating for program by user as program_rating %}

  """
  tokens = token.contents.split()
  tag_name = tokens[0]
  if len(tokens) != 7:
    raise template.TemplateSyntaxError, '%r tag requires 6 arguments' % tag_name
  if tokens[1] != 'for':
    raise template.TemplateSyntaxError, "%r tag's first argument must be 'for'" % tag_name
  if tokens[3] != 'by':
    raise template.TemplateSyntaxError, "%r tag's third argument must be 'by'" % tag_name
  if tokens[5] != 'as':
    raise template.TemplateSyntaxError, "%r tag's fourth argument must be 'as'" % tag_name
  return GetUserRatingNode(object_name=tokens[2], user=tokens[4], var_name=tokens[6])


class GetRatingNode(template.Node):
  def __init__(self, object_name, var_name):
    self.object_name, self.var_name = object_name, var_name

  def render(self, context):
    object = template.resolve_variable(self.object_name, context)
    rating = RatedItem.objects.get_for_object(object)
    context[self.var_name] = rating
    return ''


@register.tag('get_rating')
def do_get_rating(parser, token):
  """
  Syntax::

    {% get_rating for [object] as [varname] %}

  Example usage::

    {% get_rating for program as program_rating %}

  """
  tokens = token.contents.split()
  tag_name = tokens[0]
  if len(tokens) != 5:
    raise template.TemplateSyntaxError, '%r tag requires 5 arguments' % tag_name
  if tokens[1] != 'for':
    raise template.TemplateSyntaxError, "%r tag's second argument must be 'for'" % tag_name
  if tokens[3] != 'as':
    raise template.TemplateSyntaxError, "%r tag's fourth argument must be 'as'" % tag_name
  return GetRatingNode(object_name=tokens[2], var_name=tokens[4])


class RateFormNode(template.Node):
  def __init__(self, object_name):
    self.object_name = object_name

  def render(self, context):
    object = template.resolve_variable(self.object_name, context)
    ctype_id, obj_id = get_target_for_object(object)
    t = get_template('rating/rating_form.html')
    c = context
    c.update({'ctype_id': ctype_id, 'obj_id': obj_id, 'object':object })
    return t.render(c)
                                                 


@register.tag('rating_form')
def do_rating_form(parser, token):
  """
  Syntax::

    {% rating_form for [object] %}

  Example usage::

    {% rating_form for program %}

  """
  tokens = token.contents.split()
  tag_name = tokens[0]
  if len(tokens) != 3:
    raise template.TemplateSyntaxError, '%r tag requires 3 arguments' % tag_name
  if tokens[1] != 'for':
    raise template.TemplateSyntaxError, "%r tag's second argument must be 'for'" % tag_name
  return RateFormNode(object_name=tokens[2])


class RatingNode(template.Node):
  def __init__(self, object_name):
    self.object_name = object_name

  def render(self, context):
    object = template.resolve_variable(self.object_name, context)
    ctype_id, obj_id = get_target_for_object(object)
    t = get_template('rating/rating.html')
    c = context
    c.update({'ctype_id': ctype_id, 'obj_id': obj_id, 'object':object })
    return t.render(c)

@register.tag('rating')
def do_rating_form(parser, token):
  """
  Syntax::

    {% rating for [object] %}

  Example usage::

    {% rating= for program %}

  """
  tokens = token.contents.split()
  tag_name = tokens[0]
  if len(tokens) != 3:
    raise template.TemplateSyntaxError, '%r tag requires 3 arguments' % tag_name
  if tokens[1] != 'for':
    raise template.TemplateSyntaxError, "%r tag's second argument must be 'for'" % tag_name
  return RatingNode(object_name=tokens[2])