# listgender.py
#

import sys
import gender_guesser.detector as gender
g = gender.Detector()

print (g.get_gender("Jaewon"))
print (g.get_gender("Ji-won"))

print("	exiting...")
sys.exit()

