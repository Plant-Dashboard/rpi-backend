#!/bin/bash
from datetime import datetime
import Adafruit_DHT
import schedule
from pymongo import MongoClient

# Read temperature and humidity from the DHT11 sensor.
# Keeps trying to read if any values come back None
# Prints number of tries in the console and return sensor values
def readDHT11():
    sensor = 11
    pin = 4
    humidity = None
    temperature = None
    count = 0
    while humidity is None or temperature is None:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        count = count + 1

    temperature = temperature * 9.0 / 5.0 + 32
    print("Read DHT sensor attempts: {0}".format(count))
    return (humidity, temperature)


# Save values to the database in a new document
def writeToDatbase(collection, data):
    post = {
        "temperature": data["temp"],
        "humidity": data["rh"],
        "readingTime": datetime.utcnow(),
        "createdAt": datetime.utcnow(),
    }
    id = collection.insert_one(post).inserted_id
    print("Wrote to database: {0} at {1} \n".format(id, datetime.now()))


# Continuous  loop that reads the DHT11 sensor values, prints them to the console and saves them in the database every 10 minutes.
def Monitor():
    temp = 0
    humidity = 0

    readingCount = 1

    client = MongoClient("<ConnectionString>")

    db = client["<Database>"]
    collection = db.readings

    schedule.every(10).minutes.do(
        lambda: writeToDatbase(collection, {"temp": temp, "rh": humidity})
    )
    try:
        while True:
            print("Reading #{0} ".format(readingCount))
            humidity, temp = readDHT11()
            print("Humidity: {0} %".format(int(humidity)))
            print("Temperature: {0} F\n".format(int(temp)))
            schedule.run_pending()
            readingCount = readingCount + 1
    except KeyboardInterrupt:
        print("\Exiting...\n")


if __name__ == "__main__":
    Monitor()
