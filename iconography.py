import cv2 as cv
import easyocr
import os
import time
import re

# Captring device screenshot and telephony output using ADB Commands

# PART - 1: Obtaining network type from screenshot
os.system(r"adb shell screencap -p /sdcard/screen_adb.png")
time.sleep(1)
os.system(r"adb pull /sdcard/screen_adb.png screenshot_adb.png")
time.sleep(2)
os.system(r"adb shell dumpsys telephony.registry > telephony_out.txt")
time.sleep(1)

filepath = 'screenshot_adb.png'
network = 'No Network type detected'

# Cropping image to extract notification bar using OpenCV and saving it as .jpg file
img = cv.imread(filepath)
print('Filename: ', filepath)
height = img.shape[0]
width = img.shape[1]
# cv.imshow(filepath, img)
if height%2 == 0:
    new_height = int(height/2)
else:
    new_height = int((height-1)/2)
if width % 2 == 0:
    new_width = int(width/2)
else:
    new_width = int((width-1)/2)
cropped_img = img[0:100, new_width:width]
height = cropped_img.shape[0]
width = cropped_img.shape[1]
filename = filepath.split('.', 1)[0] + '_cropped.jpg'
cv.imwrite(filename, cropped_img)

# Reading Notification bar using easyocr library
reader = easyocr.Reader(['en'])                            #Reading only English 'en' alphanumeric characters
result = reader.readtext(filename, detail = 0)
# print('Result: ', result)
for text in result:
    if '4G' in text:
        network = '4G'
        continue
    if '5G' in text:
        network = '5G'
        continue
    if 'LTE' in text:
        network = 'LTE'
    
print('Network: ', network)
#End of part-1

# PART - 2: Obtaining network strength from telephony output
myFile = open("telephony_out.txt", "rt")
contents = myFile.readlines()
myFile.close()

signal_lines = []

# Storing mSignalStrength lines in a list
for text in contents:
    if "mSignalStrength" in text:
        signal_lines.append(text)
if not signal_lines:
    print("No mSignalStrength parameters received!!!")
    exit()

patterns = ['level=\d','level = \d']
lte_pattern = 'mLte'
nr_pattern = 'mNr'                         

# Note: If you want to find 4G signal strength value, you might have to change/add/remove possible patterns, and definitely change the nr_pattern 

# Searching for above patterns in each mSignalStrength lines
for signal_line in signal_lines:
    nr_found = False
    lte_found = True
    if lte_pattern in signal_line:
        waste, signal_line_lte = signal_line.split(lte_pattern, 1)
        signal_line_lte = signal_line_lte.split(',', 1)[0]                   # We again split at comma to remove NR part
        lte_found = True
    if nr_pattern in signal_line:
        waste, signal_line_nr = signal_line.split(nr_pattern, 1)
        nr_found = True
        # print('Signal line: ', signal_line)

    if not lte_found:
        print('No 4G signal found!!!')
        continue
    if not nr_found:
        print("No 5G signal detected!!!")
        continue

    no_level_found = True
    for pattern in patterns:
        result_lte = re.findall(pattern, signal_line_lte)     # result is a list of all patterns found in a string
        result_nr = re.findall(pattern, signal_line_nr)
        if result_lte:
            no_level_found = False
            levels_str = ""
            for x in result_lte:
                levels_str += x
                temp = re.findall("\d", levels_str)
                levels = list(map(int, temp))
                temp = 0
                if max(levels) > temp:
                    temp = max(levels)
                print("LTE signal bar level is: {} | ".format(temp), end='')
        if result_nr:
            no_level_found = False
            levels_str = ""
            for x in result_nr:
                levels_str += x
                temp = re.findall("\d", levels_str)
                levels = list(map(int, temp))
                temp = 0
                if max(levels) > temp:
                    temp = max(levels)
                print("NR signal bar level is: {} | ".format(temp), end='')
    if no_level_found:
        temp = signal_line.split(" ")
        vals = []
        for i in temp:
            if i.lstrip("-").isdigit():
                vals.append(i)
        if not vals:
            print("No signal strength detected!!!")
            break
        signalStr = int(vals[8])
        print('Signal strength is: ', signalStr)