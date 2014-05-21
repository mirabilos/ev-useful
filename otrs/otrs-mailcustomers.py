#!/usr/bin/env python2
# ~*~ coding: utf-8 ~*~

# OTRS Customer Mailing Helper Script
#
# Copyright © 2014, Dominik George <d.george@tarent.de>
#                   tarent solutions GmbH <info@tarent.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import sys
import SOAPpy

class SOAPProxy(SOAPpy.SOAPProxy):
    """Wrapper class for SOAPpy.SOAPProxy

    Designed so it will prepend the namespace to the action in the SOAPAction
    HTTP headers.
    """

    def __call(self, name, args, kw, ns = None, sa = None, hd = None, ma = None):
        ns = ns or self.namespace
        sa = sa or self.soapaction

        # Only prepend namespace if no soapaction was given.
        if ns and not sa:
            sa = '%s#%s' % (ns, name)

        return SOAPpy.SOAPProxy.__call(self, name, args, kw, ns, sa, hd, ma)

# Configure SOAP access to OTRS
soap_url = raw_input("SOAP - URL: ")
soap_ns = "/Core"
soap_user = raw_input("SOAP - Username: ")
soap_password = raw_input("SOAP - Password: ")
otrs_except_mail_empty = True

# Read OTRS usage details
user_name = raw_input("OTRS - Username: ")

# Read ticket details
ticket_title = raw_input("Ticket - Title: ")
ticket_from = raw_input("Ticket - From: ")
ticket_queue = raw_input("Ticket - Queue: ")
ticket_body = ""
line = ""
print("Ticket - Body (end with . on a line")
while not line == ".":
    line = raw_input("")
    if not line == ".":
        ticket_body += line + "\n"
print("")
otrs_except_mail = []
line = "."
print("Recipients - enter email exceptions one per line, end with empty line")
while not line == "":
    line = raw_input("")
    if line.strip():
        otrs_except_mail.append(line.strip())

print("Connecting via SOAP to %s as %s, using %s ..." % (soap_url, soap_user, soap_ns))

# Connect and configure SOAP Proxy
soap_proxy = SOAPProxy(soap_url, soap_ns)

def otrs_dispatch(otrs_object, otrs_function, *args):
    """ Wrapper to dispatch a request to OTRS """
    return soap_proxy.Dispatch(soap_user, soap_password, otrs_object, otrs_function, *args)

def naturalsort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)

def zipstruct(s):
    """ Create a dict from a SOAPProxy struct type as returned by OTRS """
    l = [s[k] for k in naturalsort(s._keys())]
    return dict(zip(l[::2], l[1::2]))

print("Retrieving your User ID ...")

# Retrieve numeric user id from OTRS
user_id = otrs_dispatch("UserObject", "UserLookup", "UserLogin", user_name)

if not user_id:
    print("COULD NOT GET YOUR USER ID!")
    exit(1)

print("Retrieving list of all customer users ...")

# Retrieve a list of all customer users
res = otrs_dispatch("CustomerUserObject", "CustomerUserList")

# Retrieve user details for every user name and build data structure
users = {}
uids = dict(zipstruct(res)).keys()
count = 0
for uid in uids:
    count += 1

    sys.stdout.write("\rRetrieving user details: %d / %d (%d skipped) ..." % (count, len(uids), count - len(users)))
    sys.stdout.flush()

    # Retrieve detailed user info via SOAP
    res = otrs_dispatch("CustomerUserObject", "CustomerUserDataGet", "User", uid)
    data = zipstruct(res)

    # Check exceptions
    skip = False
    for e in otrs_except_mail:
        if e and data["UserEmail"].strip().endswith(e.strip()):
            skip = True
    if otrs_except_mail_empty and data["UserEmail"].strip() == "":
        skip = True
    if skip:
        continue

    # Add zipped form to users table
    users[uid] = data

print("")
print("")

# Safety check for recipients
for user in users:
    # Sanity check
    skip = False
    for field in ["UserEmail", "UserLogin", "UserCustomerID", "UserID"]:
        if not field in users[user].keys():
            print("ERROR: %s lacks %s!" % (user, field))
            skip = True
    if skip:
        continue

    print("%s\t%s\t%s" % (users[user]["UserLogin"], users[user]["UserEmail"], users[user]["UserCustomerID"]))

# Let user decide if they want to bug all those users
print("")
ret = raw_input("The users above will receive a mailing. Type OK if you so desire: ")
if not ret == "OK":
    exit(3)

for user in users:
    # Sanity check
    skip = False
    for field in ["UserEmail", "UserLogin", "UserCustomerID", "UserID"]:
        if not field in users[user].keys():
            print("ERROR: %s lacks %s!" % (user, field))
            skip = True
    if skip:
        continue

    sys.stdout.write("Dispatching message to %s ... number ... " % user)
    sys.stdout.flush()

    # Get a new shining ticket number
    ticket_number = otrs_dispatch("TicketObject", "TicketCreateNumber")

    # Bail out if we did not get a ticket number
    if not ticket_number:
        print("ERROR!")
        continue

    sys.stdout.write("id ...")
    sys.stdout.flush()

    # Open a new ticket to contain the conversation
    ticket_id = otrs_dispatch("TicketObject", "TicketCreate",
        "TN", ticket_number,
        "Title", ticket_title,
        "Queue", ticket_queue,
        "Lock", "unlock",
        "Priority", "3 normal",
        "State", "new",
        "CustomerID", users[user]["UserCustomerID"],
        "CustomerUser", users[user]["UserLogin"],
        "OwnerID", user_id,
        "ResponsibleID", user_id,
        "UserID", user_id)

    # Bail out if we did not get a ticket ID
    if not ticket_id:
        print("ERROR!")
        continue

    sys.stdout.write("subject ... ")
    sys.stdout.flush()

    # Build an OTRS compatible mail subject to trace replies
    ticket_subject = otrs_dispatch("TicketObject", "TicketSubjectBuild",
        "TicketNumber", ticket_number,
        "Subject", ticket_title,
        "Type", "New",
        "NoCleanup", 1)

    sys.stdout.write("article ... ")
    sys.stdout.flush()

    # Bail out if we did not get a cool subject
    if not ticket_subject:
        print("ERROR!")
        continue

    # Send an article in the new ticket to inform the customer
    article_id = otrs_dispatch("TicketObject", "ArticleSend",
        "TicketID", ticket_id,
        "ArticleType", "email-external",
        "SenderType", "agent",
        "From", ticket_from,
        "To", users[user]["UserEmail"],
        "Subject", ticket_subject,
        "Body", ticket_body,
        "Charset", "utf-8",
        "MimeType", "text/plain",
        "Loop", 0,
        "NoAgentNotify", 1,
        "HistoryType", "EmailCustomer",
        "HistoryComment", "-",
        "UserID", user_id)

    # Bail out if we did not get an article ID
    if not article_id:
        print("ERROR!")
        continue

    sys.stdout.write("state ... ")
    sys.stdout.flush()

    # Set the state to auto close successful to get rid of it should there be no feedback
    ret = otrs_dispatch("TicketObject", "TicketStateSet",
        "TicketID", ticket_id,
        "State", "pending auto close+",
        "UserID", user_id)

    # Detect error on state change, but do not bail out
    if not ret:
        print("ERROR!")
    else:
        print("DONE!")

print("Script run finished!")
