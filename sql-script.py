## MODULES ##
import random
import names
import datetime as dt
import pandas as pd
import sqlite3

## FUNCTIONS AND MISC DATA GENERATION ##
def checkSum(num):
    # Converts a 4 digit number into a 5 digit checksum
    numString = str(num)
    checkNum = str(3 * (int(numString[0]) + int(numString[2])) + 7 * (int(numString[1]) + int(numString[3])))[-1]
    numString += checkNum
    return int(numString)

def randomDateString():
    # Generates a random date between two dates
    minDate = dt.date(2015,1,1)
    maxDate = dt.date(2022,10,1)
    dateRange = (maxDate - minDate).days
    randRange = minDate + dt.timedelta(days=random.randrange(dateRange))
    return randRange.strftime("%Y-%m-%d")

def randomDayAdder(maxYear, yearIn):
    # Adds a random amount of days to a date
    date = dt.datetime.strptime(yearIn, "%Y-%m-%d")
    if date.year < maxYear:
        return (date + dt.timedelta(days=random.randint(4,20))).strftime("%Y-%m-%d")
    else:
        return None

# List of genres
genreList = ["Horror","Comedy","Thriller","Fantasy","Non-Fiction","Cooking","History"]

# List of residences
residences = ["Como","Subiaco","Fremantle","Rockingham","Midland","Maylands","Joondalup","Kingsley"]

## SAMPLE DATA GENERATION ##
# Create sample data for BookEdition
isbn = [checkSum(n) for n in random.sample(range(1000,10000), 100)]
author = [names.get_full_name() for n in range(100)]
publicationDate = [random.randint(1900,2022) for n in range(100)]
genre = [genreList[random.randint(0,len(genreList)-1)] for n in range(100)]

BookEdition = pd.DataFrame(list(zip(isbn,author,publicationDate,genre)),
                          columns=["ISBN","author","publicationDate","genre"])

# Create sample data for BookCopy
isbn_copy = [isbn[random.randint(0,len(isbn)-1)] for n in range(200)]
copyNumber = [isbn_copy[0:i+1].count(item) for i, item in enumerate(isbn_copy)]
daysLoaned = [0] * len(isbn_copy)

BookCopy = pd.DataFrame(list(zip(isbn_copy,copyNumber,daysLoaned)),
                       columns=["ISBN","copyNumber","daysLoaned"])

# Create sample data for Client
clientId = [i+1 for i in range(60)]
name = [names.get_full_name() for n in range(60)]
residence = [residences[random.randint(0,len(residences)-1)] for n in range(60)]

Client = pd.DataFrame(list(zip(clientId,name,residence)),
                     columns=["clientId","name","residence"])

# List of tuples ensures ISBN and copyNumber are consistent and not mismatched during random selection
isbn_copyNumber = [list(zip(isbn_copy,copyNumber))[random.randint(0,len(isbn_copy)-1)] for n in range(500)]

clientId_loan = [clientId[random.randint(0,59)] for n in range(500)]
isbn_loan = [item[0] for item in isbn_copyNumber]
copyNumber_loan = [item[1] for item in isbn_copyNumber]
dateOut = [randomDateString() for n in range(500)]
dateBack = ["NULL" for n in range(500)]

loan = pd.DataFrame(list(zip(clientId_loan,isbn_loan,copyNumber_loan,dateOut,dateBack)),
                   columns=["clientId","ISBN","copyNumber","dateOut","dateBack"])

## SQL DATABASE INSERTION AND UPDATING ##
# Connect to the sqlite database
db = input("Enter database name here including .db extension (i.e., myDatabase.db): ")
conn = sqlite3.connect(db)
cursor = conn.cursor()

# Populate BookEdition table with sample data
BookEdition.to_sql(name="BookEdition", con=conn, if_exists="append", index=False)

#Populate BookCopy table with sample data
BookCopy.to_sql(name="BookCopy", con=conn, if_exists="append", index=False)

# Populate Client table with sample data
Client.to_sql(name="Client", con=conn, if_exists="append", index=False)

# Commit to adding sample data
conn.commit()

# Generate a list of random return dates for some loans
newDateBack = [randomDayAdder(2022, date) for date in dateOut]

# Row wise simultaneous insertion and update of loan table, see note () in readme for the reason this is done
for i, items in enumerate(loan.itertuples()):
    insert = f"INSERT INTO loan ('clientId','ISBN','copyNumber','dateOut','dateBack') VALUES ({items[1]},'{items[2]}',{items[3]},'{items[4]}',{items[5]});"
    cursor.execute(insert)
    conn.commit()
    if newDateBack[i]:
        update = f"UPDATE loan SET dateBack = '{newDateBack[i]}' WHERE clientId = {items[1]} AND ISBN = '{items[2]}' AND copyNumber = {items[3]} AND dateOut < '{newDateBack[i]}' AND dateBack IS NULL"
        cursor.execute(update)
        conn.commit()

## END OF SCRIPT ##
print("If you're reading this, your sqlite tables should have succesfully been inserted/modified")
