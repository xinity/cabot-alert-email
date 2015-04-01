from os import environ as env

from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.template import Context, Template

from cabot.cabotapp.alert import AlertPlugin

import requests
import logging

email_service_template = """Service {{ service.name }} {{ scheme }}://{{ host }}{% url 'service' pk=service.id %} {% if service.overall_status != service.PASSING_STATUS %}alerting with status: {{ service.overall_status }}{% else %}is back to normal{% endif %}.
{% if service.overall_status != service.PASSING_STATUS %}
CHECKS FAILING:{% for check in service.all_failing_checks %}
  FAILING - {{ check.name }} - Type: {{ check.check_category }} - Importance: {{ check.get_importance_display }}{% endfor %}
{% if service.all_passing_checks %}
Passing checks:{% for check in service.all_passing_checks %}
  PASSING - {{ check.name }} - Type: {{ check.check_category }} - Importance: {{ check.get_importance_display }}{% endfor %}
{% endif %}
{% endif %}
"""
email_instance_template = """Instance {{ instance.name }} {{ scheme }}://{{ host }}{% url 'instance' pk=service.id %} {% if instance.overall_status != instance.PASSING_STATUS %}alerting with status: {{ instance.overall_status }}{% else %}is back to normal{% endif %}.
{% if instance.overall_status != instance.PASSING_STATUS %}
CHECKS FAILING:{% for check in instance.all_failing_checks %}
  FAILING - {{ check.name }} - Type: {{ check.check_category }} - Importance: {{ check.get_importance_display }}{% endfor %}
{% if instance.all_passing_checks %}
Passing checks:{% for check in service.all_passing_checks %}
  PASSING - {{ check.name }} - Type: {{ check.check_category }} - Importance: {{ check.get_importance_display }}{% endfor %}
{% endif %}
{% endif %}
"""

class EmailAlert(AlertPlugin):
    name = "Email"
    author = "Jonathan Balls"

    def service_send_alert(self, service, users, duty_officers):
        emails = [u.email for u in users if u.email]
        if not emails:
            return
        c = Context({
            'service': service,
            'host': settings.WWW_HTTP_HOST,
            'scheme': settings.WWW_SCHEME
        })
        if service.overall_status != service.PASSING_STATUS:
            if service.overall_status == service.CRITICAL_STATUS:
                emails += [u.email for u in users if u.email]
            subject = '%s status for service: %s' % (
                service.overall_status, service.name)
        else:
            subject = 'Service back to normal: %s' % (service.name,)
            t = Template(email_service_template)
            send_mail(
                subject=subject,
                message=t.render(c),
                from_email='Cabot <%s>' % env.get('CABOT_FROM_EMAIL'),
                recipient_list=emails,
        )
    def instance_send_alert(self, instance, users, duty_officers):
        emails = [u.email for u in users if u.email]
        if not emails:
            return
        c = Context({
            'service': instance,
            'host': settings.WWW_HTTP_HOST,
            'scheme': settings.WWW_SCHEME
        })
        if instance.overall_status != instance.PASSING_STATUS:
            if instance.overall_status == instance.CRITICAL_STATUS:
                emails += [u.email for u in users if u.email]
            subject = '%s status for instance: %s' % (
                instance.overall_status, instance.name)
        else:
            subject = 'Instance back to normal: %s' % (instance.name,)
            t = Template(email_instance_template)
            send_mail(
                subject=subject,
                message=t.render(c),
                from_email='Cabot <%s>' % env.get('CABOT_FROM_EMAIL'),
                recipient_list=emails,
        )
