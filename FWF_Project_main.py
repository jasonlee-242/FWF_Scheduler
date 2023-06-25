#FWF Project is a personal project I created to automatically add the next FWF talk to my Google Calendar so I wouldn't
#have to check the website for the next event. It utilizes a webscraper and the Beautiful Soup libary to get the date
#and link of the event and the Google Calendar API to add the event to my personal calendar with desired settings.

#imports
import requests as rq
import difflib as diff
from bs4 import BeautifulSoup
import re
import dateutil.parser as dparser
import datetime
import sys
from quickstart import main
import logging

logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.INFO)

URL = "https://www.neurosurgery.pitt.edu/media-resources/fridays-with-friedlander"
page = rq.get(URL)
soup = BeautifulSoup(page.content, "html.parser")
results = soup.find(id="node-1048")
text_elements = results.find("div", class_="field-body")
text = text_elements.find_all("p")

#function that splits at any whitespace character
def tokenize(s):
    return re.split("\s+", s)
#basic message to compare target message to
basicText = tokenize("The next webcast will be . You can watch the webcast at . You can also view any of our previous episodes—listed below—on our YouTube channel.")
#get the text that contains the important information
def targetText():
    #exact text of interest
    to_Extract = tokenize(text[1].text)
    logging.info(to_Extract)
    return to_Extract
#get the important information from the text
def matchSequence(text):
    #sequence matcher to find similarities between current web text and basic text
    matcher = diff.SequenceMatcher(a = text, b = basicText)
    #put the part of the text that is NOT the same into a list
    indexes = [(match.a, match.size) for match in matcher.get_matching_blocks()]
    keyText = [' '.join((text[sum(indexes[loc]):indexes[loc+1][0]])) for loc in range(len(indexes) - 1)][:-1]
    return keyText
#get event link
def eventLink():
    eventlink = text_elements.findAll('a')
    for test in eventlink:
        if test.getText()[:4] == 'http':
            return test.getText()
#get event date
def eventDate(imptext):
    try:
        grab_Date = dparser.parse(imptext[0], fuzzy = True)
        curr_Year = datetime.datetime.now().year
        eventDate = datetime.date(curr_Year, grab_Date.month, grab_Date.day)
        return eventDate
    #if there is no date published yet, exit program and return status
    except:
        sys.exit("No date available. Next event not scheduled.")
#get the topic of the event
def eventTopic():
    topic = text_elements.find('strong')
    return topic.getText()
#get the presenter
def event_presenter():
    presenter = text_elements.findAll('a')[1]
    return presenter.getText()
# #Run the program
def run():
    target = targetText()
    match = matchSequence(target)
    date = eventDate(match)
    link = eventLink()
    topic = eventTopic()
    presenter = event_presenter()
    #run the main function from quickstart.py to ask Google API to create the event
    main(date, link, topic, presenter)
run()