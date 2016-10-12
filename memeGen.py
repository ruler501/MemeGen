import os
import sys
import urllib
from PIL import Image, ImageFont, ImageDraw
from bs4 import BeautifulSoup

alertBoxes = False
try:
    import Tkinter as tk
    import tkMessageBox
    alertBoxes = True
except:
    print("Alert boxes not supported on your setup")

def create_meme(input_string):
    exclusions = []
    with open('exclude.cfg') as exclusionFile:
        for exclude in exclusionFile:
            exclusions.append(exclude.strip())
    curInd = 0
    curCount = 0
    totalX = 0
    totalY = 0
    if input_string[0] is not '^':
        input_string = '^' + input_string
    if input_string[-1] is not '$':
        input_string += '$'
    while curInd < len(input_string):
        totalChars = 0
        cardItem = None
        extraAdd = 0
        matchString = ''
        while curInd + totalChars < len(input_string):
            tMatchString = input_string[curInd:curInd+totalChars + 1]
            rUrl = 'http://gatherer.wizards.com/Pages/Search/Default.aspx?name=+[' + input_string[curInd:curInd+totalChars + 1] + ']'
            if input_string[curInd+totalChars] == ' ':
                if totalChars == 0:
                    curInd += 1
                    continue
                else:
                    break
            elif input_string[curInd+totalChars] == '^':
                if totalChars > 0:
                    continue
                else:
                    totalChars = 1
            elif input_string[curInd+totalChars] == '$' and totalChars == 0:
                raise Exception("Couldn't find '"+ tMatchString[:-1] + "' at the end of a card name.\nThis can sometimes be fixed by adding a space before the last character")
            if input_string[curInd] == '^':
                rUrl = 'http://gatherer.wizards.com/Pages/Search/Default.aspx?name=+[m/' + input_string[curInd:curInd+totalChars + 1] + '/]'
                tMatchString = input_string[curInd + 1:curInd+totalChars + 1]
            if input_string[curInd+totalChars] == '$':
                rUrl = 'http://gatherer.wizards.com/Pages/Search/Default.aspx?name=+[m/' + input_string[curInd:curInd+totalChars + 1] + '/]'
                tMatchString = input_string[curInd:curInd+totalChars]

            req = urllib.urlopen(rUrl)
            doc = BeautifulSoup(req.read(), "lxml")
            req.close()
            cardItems = doc.find_all(**{"class": "cardItem evenItem"})
            cardItems += doc.find_all(**{"class": "cardItem oddItem"})
            if len(cardItems) > 0:
                for tCardItem in cardItems:
                    cardImage = tCardItem.find_all("img")[0]
                    name = cardImage["alt"]
                    if name.find('//') >= 0 or name in exclusions:
                        continue
                    if input_string[curInd+totalChars] == '$':
                        if name.lower().rfind(tMatchString) >= 0:
                            cardItem = tCardItem
                            matchString = tMatchString
                            totalChars += 1
                            break
                    else:
                        if name.lower().find(tMatchString) >= 0:
                            cardItem = tCardItem
                            totalChars += 1
                            matchString = tMatchString
                            break
                else:
                    break
            else:
                break
        if totalChars < 1 or cardItem == None:
            raise Exception("Can't succeed, couldn't find '" + input_string[curInd] + "'")
        cardImage = cardItem.find_all("img")[0]
        name = cardImage["alt"]
        url = "http://gatherer.wizards.com/" + cardImage["src"][6:]
        print(input_string[curInd:curInd+totalChars])
        print(url)
        urllib.urlretrieve(url, "Image"+ str(curCount) + ".jpg")
        img = Image.open("Image" + str(curCount) + ".jpg")
        font = ImageFont.truetype("beleren-bold-webfont.ttf", img.size[1]/25)
        draw = ImageDraw.Draw(img)
        fChar = name.lower().index(matchString)
        if input_string[curInd+totalChars-1] == '$':
            fChar = name.lower().rindex(matchString)
        fSize = draw.textsize(name[:fChar], font=font)
        if input_string[curInd] == '^':
            fSize = -18, fSize[1]
        sSize = draw.textsize(name[:fChar+len(matchString)], font=font)
        if totalChars + curInd >= len(input_string):
            sSize = img.size[0] - 18, sSize[1]
        totalX += sSize[0] - fSize[0]
        totalY = max(img.size[1], totalY)
        img3 = img.crop((18 + fSize[0], 0, 18 + sSize[0], img.size[1]))
        img3.save("Cropped" + str(curCount) + ".jpg")
        curInd += totalChars
        curCount += 1

    curX = 0
    finalImage = Image.new('RGB', (totalX, totalY))
    for i in range(curCount):
        img = Image.open("Cropped" + str(i) + ".jpg")
        finalImage.paste(img, (curX, 0))
        curX += img.size[0]

    finalImage.save("Result.jpg")
    print("Saved result to " + os.getcwd() + "/Result.jpg enjoy your memes")
    root = tk.Tk()
    root.withdraw()
    tkMessageBox.showinfo("Finished Meme Generation", "Saved result to " + os.getcwd() + "/Result.jpg enjoy your memes")

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        create_meme(' '.join(sys.argv[1:]).lower())
    else:
        print "Usage:\npython memeGen.py <input text>"
