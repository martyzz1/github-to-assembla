#!/usr/bin/env python
import os
import re
from github3 import login

from assembla import API, Ticket, TicketComment

GITHUB_USER = os.environ.get("GITHUB_USER", "")
GITHUB_PASS = os.environ.get("GITHUB_PASS", "")

ASSEMBLA_KEY = os.environ.get("ASSEMBLA_KEY", "")
ASSEMBLA_SECRET = os.environ.get("ASSEMBLA_SECRET", "")
ASSEMBLA_SPACE = os.environ.get("ASSEMBLA_SPACE", "")

GITHUB_AUTHOR = os.environ.get("GITHUB_AUTHOR", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "")

gh = login(GITHUB_USER, password=GITHUB_PASS)

assembla = API(
    key=ASSEMBLA_KEY,
    secret=ASSEMBLA_SECRET,
)
repo = 'migreat'


def get_assembla_issues(my_space):
    existing = {}

    #for ticket in my_space.tickets(extra_params={'tags': 'test'}):
    for ticket in my_space.tickets():
        print u'#{0} - {1}, {2}, {3}'.format(ticket['number'], ticket['summary'], ticket['reporter_id'], ticket['assigned_to_id'])
        got_tag = 0
        tags = ticket.tags()
        for tag in tags:
            #print tag['name']
            if tag['name'] == GITHUB_REPO:
                    got_tag = 1
        if got_tag == 1:
            #print "Got a {0} tagged ticket {1}".format(GITHUB_REPO, ticket['number'])
            if ticket['summary'].startswith('[#'):
                print "Found previously merged issue {0}".format(ticket['number'])
                g_num = re.findall(r'^\[#(.*?)\]', ticket['summary'])
                if g_num:
                    print "Positive match {0}".format(g_num)
                    existing[g_num[0]] = ticket
        else:
            pass
            #print "{0} tag not found in Ticket's tags - {1}".format(GITHUB_REPO, tags)

    return existing


def get_user_info(gh, my_space):
    """
    Use this to help you extract the github users and assembla users, so you can setup the usermap
    """
    users = my_space.users()
    for user in users:
        print user['id'], user['login']

    repo = gh.repository(GITHUB_AUTHOR, GITHUB_REPO)
    for user in repo.iter_assignees():
        print user.login


def get_github_issues(gh):
    gissues = gh.iter_repo_issues(GITHUB_AUTHOR, GITHUB_REPO, state='open')

    return gissues


def get_assembla_user_id(github_login):
    usermap = {
            '<github.login>': '<assembla.id>',
    }

    if github_login in usermap:
        return usermap[github_login]
    assert False, "User not found in assembla {0}".format(github_login)

if __name__ == "__main__":

    #get_user_info(gh, my_space)
    gh_issues = get_github_issues(gh)
    my_space = assembla.spaces(name=ASSEMBLA_SPACE)[0]
    tags = my_space.tags()

    as_existing_issues = get_assembla_issues(my_space)

    for g_issue in gh_issues:
        if hasattr(g_issue, 'pull_request') and g_issue.pull_request:
            #ignore pullrequests
            print "Ignoring pullrequest {0}".format(g_issue.number)
            continue
        num = unicode(g_issue.number)
        print "Does {0} exist already?".format(num)
        ticket = None
        if num in as_existing_issues:
            print "{0} already exists - Will only update comments".format(num)
            ticket = as_existing_issues[num]
        else:
            labels = g_issue.iter_labels()
            data = {
                        'description': g_issue.body_text,
                        'summary': u"[#{0}] {1}".format(num, g_issue.title),
                        'priority': None,
                    }

            if g_issue.assignee:
                assigned_to_id = unicode(get_assembla_user_id(g_issue.assignee.login))
                data['assigned_to_id'] = assigned_to_id
            reporter = g_issue.user.login
            reporter_id = get_assembla_user_id(reporter)
            print "reporter = {0}, {1}".format(reporter, reporter_id)
            data['reporter_id'] = unicode(reporter_id)
            data['followers'] = [reporter_id, ]
            tags = [GITHUB_REPO, ]
            for label in labels:
                tags.append(label.name)
                # migrate P1, P2 .. P5 labels to assembla priorities.
                for p in [1, 2, 3, 4, 5]:
                    print label.name
                    if label.name == 'P{0}'.format(p):
                        print "Got priority label {0}".format(label.name)
                        data['priority'] = p

            data['tags'] = tags

            print "Creating ticket for {0}".format(num)
            nticket = Ticket(data)
            nticket.space = my_space

            ticket = nticket.write()
            print "Created ticket with {0} and {1}, {2}".format(ticket['id'], ticket['number'], ticket['reporter_id'])
        ticketcomments = ticket.comments()
        print ticketcomments
        issue_comments = g_issue.iter_comments()
        count = 0
        for ic in issue_comments:
            if len(ticketcomments) > count + 1:
                tc = ticketcomments[count + 1]
                print tc['created_on']
                print tc['ticket_changes']
                print tc['updated_at']
                print tc['ticket_id']
                print tc['id']
                print tc['user_id']
                if tc['comment'] == ic.body:
                    pass
                else:
                    print "comments diverged. Ignoring"
                    break

            else:
                print "No comment exists lets create it"
                user_id = unicode(get_assembla_user_id(ic.user.login))
                comment = ic.body
                data = {
                            "user_id": user_id,
                            "comment": comment,
                        }

                tcomment = TicketComment(data)
                tcomment.ticket = ticket
                tcomment = tcomment.write()
            count += 1
