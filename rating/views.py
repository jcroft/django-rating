from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from rating.models import RatedItem

@csrf_exempt
def rate(request):
  
  RATING_MAPPING = {
    '1': "one",
    '2': "two",
    '3': "three",
    '4': "four",
    '5': "five",
  }
  
  if request.method == 'POST' and request.user.is_authenticated():
    try:
      target =  request.POST['target']
      content_type_id, object_id = target.split(':')
    except KeyError:
      raise Http404, 'Target object not provided (you are probably a spam bot).'
      
    try:
      object = ContentType.objects.get(pk=content_type_id).get_object_for_this_type(pk=object_id)
    except ObjectDoesNotExist:
      raise Http404, 'Target object does not exist.'
    
    try:
      rating = request.POST['rating']
      rated_item = RatedItem.objects.add_or_update_rating(object, rating, request.user)
      success="true"
    except KeyError:
      success = "false"
      rated_item = None
    
    if request.is_ajax():
      if rated_item:
        context = "{'success': '%s', 'object_rated_id': '%s', 'user_rated_id': '%s', 'new_rating': '%s', 'user_rating': '%s' }" % (success, rated_item.object.pk, request.user.id, rated_item.rating_average, rating)
      else:
        context = "{'success': '%s', 'user_rated_id': '%s', 'user_rating': '%s' }" % (success, rated_item.pk, request.user.id, rating)
      try:
        request.user.get_and_delete_messages()
      except:
        pass
      return HttpResponse(context, mimetype="application/json")
      
    else:
      if rated_item:
        message = "Your rating was has been recorded. You gave %s %s out of five stars." % (unicode(rated_item.object), RATING_MAPPING[rating])
        messages.success(request,  message)
        return HttpResponseRedirect("%s#rating-form-%s" %(request.META['HTTP_REFERER'], object.id))
      else:
        message = "You did not choose a star value, so your vote was not recorded."
        messages.error(request, message)
        return HttpResponseRedirect("%s#rating-form-%s" %(request.META['HTTP_REFERER'], object.id))
        
  else:
    raise Http404, 'This URL only accepts POSTs from registered users.'
