from itertools import combinations_with_replacement
from string import ascii_letters, digits
import time
import csv
import random
import serial

# ATE1 will enable echo, ATE0 to disable
# https://github.com/danielewood/sierra-wireless-modems
# 4117727_AirPrime_EM74xx-MC74xx_AT_Command_Reference_r3.pdf says:

fieldnames = ["pw", "ATresponse"] # csv

start = time.time() # csv

characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

# Password length: 4–10 characters (0–9, A–Z, upper or lower case)
# 5 = about 65MB/250MB in size if txt/csv
# 6 = about 825MB in size if txt 
max_length = 4 # takes 3 hours on a laptop

def main():

    def writecsv(genyield):
        firstrow = [
            {"pw": "Start: {}".format(start),
            "ATresponse": "dummystartvalue"}
            ]
        with open("list.csv", "a", newline="") as file:
            writer = csv.DictWriter(
                file, fieldnames=fieldnames
                )
            writer.writeheader()
            writer.writerows(firstrow)
        
        with open("list.csv", "a", newline="") as file:
            writer = csv.DictWriter(
                file, fieldnames=fieldnames
                )
            for item in genyield:
                writer.writerows(
                    [
                    {
                    "pw": item,
                    "ATresponse": "dummygeneratorvalue"
                    }
                    ]
                )
            lastrow = [
                {
                "pw": "End: {}".format((time.time() - start)),
                "ATresponse": "dummyendvalue"
                }
                ]
            writer.writerows(lastrow)

    def writefile(genyield):
        with open("file.txt", "a") as file:
            for item in genyield:
                file.write(item + "\n")
            
    def mygen():
        # random.choices(ascii_letters + digits, k=10)
        for subsequence_length in range(1, max_length+1): 
            for combo in combinations_with_replacement(
                ascii_letters + digits, r=4): # min pw len = 4
                # otherwise: r=subsequence_length
                # temp = ''.join(random.choices(combo, k=max_length)) # no generator advantage here
                temp = ''.join(combo)
                # yield [{"pw": temp, "ATresponse": "dummygeneratorvalue"}]
                yield temp
                
    def myserialcommunicator(genyield):
        with serial.Serial(
            'COM6', 115200, timeout=0.017
            ) as ser: # 0.02 > sweetspot > 0.017
            #sendstring = str.encode('AT\r')
            #ser.write(sendstring)
            #response =  ser.read(7)
            #if "OK" in str(response):
            #    print("OK in response for AT")
            #    print(response)
            ## sendstring = str.encode('AT!ENTERCND="A710"\r')
            for item in genyield:
                # time.sleep(0.01)
                ser.flushInput()
                ser.flushOutput()
                pw_string = item
                encode_string = 'AT!ENTERCND="{}"\r'.format(
                pw_string
                )
                sendstring = str.encode(encode_string)
                # sendstring = str.encode('AT\r')
                ser.write(sendstring)
                response =  ser.read(4)
                error_counter = 0
                if "OK" in str(response):
                    print("OK in response for AT!ENTERCND")
                    print(response)
                    print("pw_was: {}".format(pw_string))
                    with open("file.txt", "a") as file:
                        file.write(str(response) + "for sendstring " + str(sendstring) + " with pw: " + pw_string + "\n")
                else:
                    print('pw_string was: {} - No OK in response to AT!ENTERCND code'.format(pw_string))
                    print(response)

    # writecsv(mygen())
    # writefile(mygen())

    myserialcommunicator(mygen())
    print(time.time() - start)

if __name__ == "__main__":
    main()
    print("Script ran standalone and was not imported.")
