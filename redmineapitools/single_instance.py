# -*- coding: utf-8 -*-
"""
    redmineapitools.single_instance
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Functions and a API wrapper class working with a single Redmine instance.
    

    :copyright: (c) 2017 by Tobias `dpausp` <dpausp@posteo.de>
    :license: BSD, see LICENSE for more details.
"""
import logging
import uuid

from redmine import Redmine
from redmineapitools.external.werkzeug import cached_property
from six import iteritems, text_type
from redmine.exceptions import ForbiddenError


logg = logging.getLogger(__name__)


def set_custom_fields(issue, cf_ids_to_values):
    cf_dict = {cf["id"]: cf["value"] for cf in list(issue.custom_fields)}
    for cf_id, value in iteritems(cf_ids_to_values):
        cf_dict[cf_id] = value
    issue.custom_fields = [dict(id=cf_id, value=value) for cf_id, value in iteritems(cf_dict)]


def get_custom_field_value_by_name(issue, custom_field_name):
    maybe_custom_field = [cf for cf in issue.custom_fields if cf.name == custom_field_name]
    if not maybe_custom_field:
        raise Exception("issue does not have the custom field " + custom_field_name)

    custom_field = maybe_custom_field[0]
    return custom_field.value


def get_category_by_name(project, category_name):
    maybe_category = [c for c in project.issue_categories if c.name == category_name]
    if not maybe_category:
        raise Exception("project does not have the category " + category_name)

    category = maybe_category[0]
    return category


def get_tracker_by_name(project, tracker_name):
    maybe_tracker = [t for t in project.trackers if t.name == tracker_name]
    if not maybe_tracker:
        raise Exception("project does not have the tracker " + tracker_name)

    tracker = maybe_tracker[0]
    return tracker


class RedmineAPIWrapper(object):
    """Stateful Redmine API wrapper 
    Caches some Redmine instance configuration objects like trackers or statuses
    and provides some convenient higher-level access methods that may depend on cached config objects."""

    CACHED_PROPERTIES = ("custom_fields", "issue_status", "trackers")

    def __init__(self, url, key=None, admin_key=None, custom_fields_to_id=None, *args, **kwargs):
        """
        Custom field definitions can only be retrieved with admin privileges. To use custom fields, you can:
        - supply a `custom_fields_to_id` dict that maps custom field names to ids
        - provide an API key with admin rights as `key`
        - provide an API key with admin rights as `admin_key` in addition to an unprivileged API key as `key`.
          The admin API key will only be used to retrieve the list of custom fields.
        """
        self.api = Redmine(url, *args, key=key, **kwargs)

        if custom_fields_to_id is not None:
            self.custom_fields_to_id = custom_fields_to_id

        if admin_key is None:
            self.admin_api = self.api
        else:
            self.admin_api = Redmine(url, *args, key=admin_key, **kwargs)

    def remove_cached(self):
        """Remove cached (possibly expensive) values"""
        for prop in RedmineAPIWrapper.CACHED_PROPERTIES:
            if prop in self.__dict__:
                del self.__dict__[prop]

    @cached_property
    def custom_fields(self):
        try:
            custom_fields = list(self.admin_api.custom_field.all())
        except ForbiddenError:
            raise Exception("API user does not have the required admin privileges!")
        return custom_fields

    @cached_property
    def custom_fields_to_id(self):
        cf_ids = {text_type(cf.name): cf.id for cf in self.custom_fields}
        return cf_ids

    @cached_property
    def issue_status(self):
        issue_status = list(self.api.issue_status.all())
        return issue_status

    def issue_status_by_name(self, status_name):
        maybe_status = [st for st in self.api.issue_status.all() if st.name == status_name]
        if not maybe_status:
            raise KeyError("status does not exist: " + status_name)
        return maybe_status[0]

    @cached_property
    def trackers(self):
        trackers = list(self.api.tracker.all())
        return trackers

    def set_custom_fields_by_name(self, issue, cf_names_to_values):
        cf_ids = self.custom_fields_to_id
        cf_ids_to_values = {cf_ids[text_type(name)]: value for name, value in iteritems(cf_names_to_values)}
        return set_custom_fields(issue, cf_ids_to_values)

    def gen_uuid_for_issue(self, iss):
        uu = uuid.uuid4()
        self.set_custom_fields_by_name(iss, {"UUID": str(uu)})
        iss.save()
        return uu
