import mysql.connector
import requests
from bs4 import BeautifulSoup


def get_combine_data(cursor, cnx):
    """
    This will get combine data from http://nflcombineresults.com/nflcombinedata.php
    and place that data into a table named WSA.nfl on the local host
    Takes a mysql connector cursor and connection object as parameters
    """

    # making the soup of combine results
    page = requests.get('http://nflcombineresults.com/nflcombinedata.php')
    soup = BeautifulSoup(page.text, 'html.parser')

    # get the list of players and their combine data
    # [1:-1] to skip the header row & end before last row
    playerRows = soup.find_all('tr')[1:-1]
    playerID = 1

    add_athlete = ("INSERT INTO NFL "
                   "(playerID, year, playerName, college, position, height, weight, dash, bench, leap, broad, shuttle, cone)"
                   "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                   )

    for player in playerRows:
        playerData = player.find_all('td')

        # need to check for empty values
        year = clean_data(playerData[0])
        name = clean_data(playerData[1])
        college = clean_data(playerData[2])
        pos = clean_data(playerData[3])
        height = clean_data(playerData[4])
        weight = clean_data(playerData[5])
        dash = clean_data(playerData[7])
        bench = clean_data(playerData[8])
        leap = clean_data(playerData[9])
        broad = clean_data(playerData[10])
        shuttle = clean_data(playerData[11])
        cone = clean_data(playerData[12])

        # send information to MySQL database
        athlete_data = (playerID, year, name, college, pos, height,
                        weight, dash, bench, leap, broad, shuttle, cone)

        cursor.execute(add_athlete, athlete_data)

        playerID += 1

    cnx.commit()

    cursor.close()
    cnx.close()

    return None


def clean_data(extracted_data):
    # handle empty values + 9.99
    if (len(extracted_data.text) > 0) and (extracted_data.text != '9.99'):
        return extracted_data.text
    else:
        return None


def main():
    # Main function to create mysql connector object run get_combine_data

    cnx = mysql.connector.connect(user="root",
                                  host="127.0.0.1",
                                  database="WSA",
                                  password="")  # insert password

    cursor = cnx.cursor()


    get_combine_data(cursor, cnx)

    # clear_table(cursor, cnx)

    # testing section don't edit
    try:
        testing_data(cursor, cnx)
    except Exception as e:
        print("Testing failed with error:")
        print(e)


def testing_data(cursor, cnx):
    ''' This is just a quick test to see if the first row of the database is correct '''

    select = "Select * from NFL where playerID = 1"
    cursor.execute(select)
    response = cursor.fetchall()[0]
    name = response[2]
    bench = response[8]

    if name == "Josh Adams" and bench == 18:
        print("Testing Passed")
    else:
        print("First Row Does Not Match")


def clear_table(cursor, cnx):
    ''' Helper Function to call in order to clear table after mistakes '''

    cursor.execute("Delete from NFL")
    cursor.execute("ALTER TABLE NFL AUTO_INCREMENT = 1")
    cnx.commit()


if __name__ == "__main__":
    main()