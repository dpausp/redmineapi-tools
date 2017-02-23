# -*- coding: utf-8 -*-
"""
    redmineapitools.multiple_instances
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Helpers dealing with multiple Redmine instances. 
    Use cases:
    
    - copy redmine issues from one instance to another


    :copyright: (c) 2017 by Tobias `dpausp` <dpausp@posteo.de>
    :license: BSD, see LICENSE for more details.
"""
import logging


logg = logging.getLogger(__name__)


def copy_issue_to_instance(src_issue, dest_redmine,
                           dest_status_name=None,
                           dest_tracker_name=None,
                           dest_assignee_name=None,
                           dest_priority_name=None,
                           dest_project_identifier=None,
                           copy_note_template="copied from {src_url}"):
    dest_issue = dest_redmine.issue.new()
    # simple attributes which can be copied
    for attr in ["description", "start_date", "due_date", "done_ratio", "subject"]:
        if attr in src_issue._attributes:
            dest_issue[attr] = src_issue[attr]
    # assignee
    src_user = src_issue.assigned_to.refresh()
    dest_user = dest_redmine.user.filter(name=src_user.mail)
    if not dest_user:
        raise Exception("no matching user found with mail address " + src_user.mail)
    dest_issue.assigned_to_id = dest_user[0].id
    # tracker
    if not dest_tracker_name:
        dest_tracker_name = src_issue.tracker.name
    dest_tracker = [t for t in dest_redmine.trackers if t.name == dest_tracker_name]
    if not dest_tracker:
        raise Exception("tracker not found for name " + dest_tracker_name)
    dest_issue.tracker_id = dest_tracker[0].id
    # status
    if not dest_status_name:
        dest_status_name = src_issue.status.name
    dest_status = [s for s in dest_redmine.issue_statuses if s.name == dest_status_name]
    if not dest_status:
        raise Exception("status not found for name " + dest_status_name)
    dest_issue.status_id = dest_status[0].id
    # priority
    if not dest_priority_name:
        dest_priority_name = src_issue.priority.name
    dest_redmine_priorities = dest_redmine.enumeration.filter(resource="issue_priorities")
    dest_priority = [p for p in dest_redmine_priorities if p.name == dest_priority_name]
    if not dest_priority:
        raise Exception("priority not found for name " + dest_priority_name)
    dest_issue.priority_id = dest_priority[0].id
    if dest_project_identifier is None:
        dest_project_identifier = src_issue.project.refresh().identifier
    try:
        dest_project = dest_redmine.project.get(dest_project_identifier)
    except:
        raise Exception("project not found for identifier " + dest_project_identifier)
    # custom fields
    dest_custom_field_descriptions = {cf.name: cf for cf in dest_redmine.custom_fields}

    def create_custom_field(cf):
        dest_cf_description = dest_custom_field_descriptions.get(cf.name)
        if dest_cf_description is None:
            raise Exception("custom field not found for name " + cf.name)
        dest_cf = dict(id=dest_cf_description.id, value=cf.value)
        return dest_cf

    dest_issue.custom_fields = [create_custom_field(cf) for cf in src_issue.custom_fields]

    dest_issue.project_id = dest_project.id
    # save it and post note with link to source issue
    dest_issue.save()
    notes = copy_note_template.format(src_url=src_issue.url)
    dest_issue.refresh()
    dest_redmine.issue.update(dest_issue.id, notes=notes)
    return dest_issue
