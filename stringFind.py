import sys
import urllib
from bs4 import BeautifulSoup

def outputMatching(input_string):
    i = 0
    count = 1
    while i < count:
        rUrl = 'http://gatherer.wizards.com/Pages/Search/Default.aspx?page=' + str(i) + '&text=+[m/' + input_string + '/]'
        req = urllib.urlopen(rUrl)
        doc = BeautifulSoup(req.read(), "lxml")
        req.close()
        cardItems = doc.find_all(**{"class": "cardItem evenItem"})
        cardItems += doc.find_all(**{"class": "cardItem oddItem"})
        tStr = str(doc.find_all(**{"class": "termdisplay"})[0].span)
        count = (int(tStr[tStr.rfind('(')+1:tStr.rfind(')')]) + 99)/100
        for cardItem in cardItems:
            cardImage = cardItem.find_all("img")[0]
            print(cardImage["alt"])
        i += 1

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        outputMatching(" ".join(sys.argv[1:]))
    else:
        print("Usage: python stringFind.py <String to find>")
