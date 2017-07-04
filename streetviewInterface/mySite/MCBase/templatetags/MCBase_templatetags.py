from django.template import Library
from MCBase.config_navbar import *
import re
from django.core.urlresolvers import reverse, NoReverseMatch
import random
register = Library()

# Returns a list containing range made from given value
# Usage (in template): {% for i in 3|get_range %}
@register.filter
def get_range( value ):
  return range( value )

@register.filter
def increment( i ):
  return i+1

# Usage: {%for a, b in first_list|zip:second_list %}
@register.filter()
def zip_lists(a, b):
  return zip(a, b)

@register.inclusion_tag('MCBase/base-navbar.html', takes_context=True)
def load_base_navbar(context):
    navbar_variables = {'website_name': website_name,
                        'left_side_nav':left_side_nav,
                        'left_side_href':left_side_href,}
    context.update(navbar_variables)
    return context

# Usage:
# {{dictionary|keyvalue:key_variable}}
@register.filter
def keyvalue(dict, key):
    return dict[key]

# Usage:
#  <li class="nav-blog {% active 'url-name' %}"><a href="#">Home</a></li>
#  <li class="nav-blog {% active '^/regex/' %}"><a href="#">Blog</a></li>
@register.simple_tag(takes_context=True)
def active(context, pattern_or_urlname):
    try:
        pattern = '^' + reverse(pattern_or_urlname)
    except NoReverseMatch:
        pattern = pattern_or_urlname
    path = context['request'].path
    if re.search(pattern, path):
        return 'active'
    return ''

# Usage
# {% for item in list|shuffle %}
#    <li>{{ item }}</li>
# {% endfor %}
@register.filter
def shuffle(arg):
    tmp = list(arg)[:]
    random.shuffle(tmp)
    return tmp
