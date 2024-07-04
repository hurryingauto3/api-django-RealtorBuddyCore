# In your Django project's settings where you configure Jinja2:
from django.templatetags.static import static
from jinja2 import Environment

def environment(**options):
    env = Environment(**options)
    env.globals['static'] = static  # Add static method globally to your Jinja2 environment
    return env
