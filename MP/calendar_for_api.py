#!/usr/bin/env python3 --noauth_local_webserver
# pip3 install google-api-python-client google-auth-httplib2 google-auth-oauthlib oauth2client httplib2

# Reference: https://developers.google.com/calendar/quickstart/python
# Documentation: https://developers.google.com/calendar/overview

# Be sure to enable the Google Calendar API on your Google account by following the reference link above and
# download the credentials.json file and place it in the same directory as this file.

from __future__ import print_function
from datetime import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import datetime

class Calendar:
    """This class includes 2 function defitions that will add or remove Google Calendar events.
    It is imported into the flask_api.py and used as part of the makeABooking() and cancelABooking() functions.
    """
    service = None

    def __init__(self):
        """inits Calendar with the scopes and credentials for Google Calendar API
        """
        # If modifying these scopes, delete the file token.json.
        SCOPES = "https://www.googleapis.com/auth/calendar"
        store = file.Storage("token.json")
        creds = store.get()

        # Examine the credentials
        if(not creds or creds.invalid):
            flow = client.flow_from_clientsecrets("credentials.json", SCOPES)
            creds = tools.run_flow(flow, store)

        self.service = build("calendar", "v3", http=creds.authorize(Http()))

    def insert(self, event):
        """This function is for adding an event into the Google Calendar.
        The event is created via flask_api.makeABooking() function.
        The event is the booking that user has made when using the application.

        Arguments:
            event {dict} -- An Google Calendar event
        """
        event = self.service.events().insert(calendarId = "primary", body = event).execute()


    def delete(self, user_id, car_id, begin_time):
        """This function is for removing an event from the Google Calendar.
        The event is created via flask_api.makeABooking() function and can be removed via flask_api.cancelABooking():
            - From the current time, a list of the future events will be returned
            - For each event in that list, they will be examined to find the correct event to remove based on the starting time and description

        Arguments:
            user_id {int} -- User ID of the user who makes the booking
            car_id {int} -- Car ID of the car which has been booked
            begin_time {datetime} -- The begining date and time of the booking
        """
        # Get a list of events from the current time
        now = datetime.datetime.now().isoformat() + '+10:00'
        events = self.service.events().list( calendarId='primary', 
                                        timeMin=now,
                                        maxResults=10, 
                                        singleEvents=True,
                                        orderBy='startTime', 
                                        timeZone='+10:00').execute()
        events = events.get("items", [])

        # Search for the right event and delete
        for event in events:
            event_start_time    = event['start']['dateTime'].replace('T', ' ').split('+')[0] # Format: '2020-05-02T10:00:00+10:00'
            begin_time          = begin_time + ":00"

            if event['description'] == f'userId: {user_id} and carId: {car_id}' and event_start_time == begin_time:
                self.service.events().delete(calendarId='primary', 
                                        eventId=event['id']).execute() # Deletion
