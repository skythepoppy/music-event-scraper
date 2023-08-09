import requests
import selectorlib
import smtplib, ssl
import os
import time
import sqlite3



# establish a connection
connection = sqlite3.connect("data.db")

# url and headers
URL = "http://programmer100.pythonanywhere.com/tours/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


# scrape page source from the URL
def scrape(url):
    """ Scrape the page source from the URL """
    response = requests.get(url, headers=HEADERS)    #
    source = response.text      # extract text from url
    return source

# extract data
def extract(source):
    extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
    value = extractor.extract(source)["tours"]
    return value

# send information to email
def send_email(message):
    host = "smtp.gmail.com"
    port = 465
    username = 'raphaelsebastien.evangelista@gmail.com'
    password = 'jujverbpptodpplg'   # google app password
    receiver = "raphaelsebastien.evangelista@gmail.com"
    my_context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host, port, context=my_context) as server:
        server.login(username, password)
        server.sendmail(username, receiver, message)

    print("Email was sent!")


# store extracted data into database
def store(extracted):
    row = extracted.split(",")
    row = [item.strip() for item in row]
    cursor = connection.cursor()    # initialize cursor object
    cursor.execute("INSERT INTO events VALUES(?,?,?)", row)
    connection.commit()

# read in data extracted from the scraped URL
def read(extracted):
    row = extracted.split(",")
    row = [item.strip() for item in row]
    band, city, date = row
    cursor = connection.cursor()    # initialize cursor object
    cursor.execute("SELECT * FROM events WHERE band=? AND city=? AND date=?", (band, city, date))  # cursor object can execute sql queries
    rows = cursor.fetchall()
    return rows


if __name__ == "__main__":
    # runs program non-stop ( in 2 second intervals)
    while True:
        scraped = scrape(URL)
        extracted = extract(scraped)
        print(extracted)


        if extracted != "No upcoming tours":
            row = read(extracted)
            if not row:
                store(extracted)
                send_email(message="New event was found!")

        time.sleep(2)