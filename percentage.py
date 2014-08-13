#! /Users/alexis/anaconda/bin/python
import re
import subprocess

def myround(x, base=5):
    return int(base * round(float(x)/base))

f = open('/Users/alexis/Developer/Media/out.log', 'r')
lines = f.readlines()
lines = lines[0].split('\r')
name = lines[0]
print name
encodes = [line for line in lines if 'Encoding' in line]
f.close()
temp_path = '/Users/alexis/Developer/Media/temp.png'
progression_path = '/Users/alexis/Developer/Media/img/{}.png'

if len(encodes) > 0:
    last = encodes[-1]
    p = re.compile('([\d]+\.[\d]{2}) %')
    m = p.findall(last)
    
    percentage = myround(m[0])
    print percentage
    progression_path = progression_path.format(percentage)
    subprocess.call(['cp', progression_path, temp_path])

    p = re.compile('([\d]{2}h[\d]{2}m[\d]{2}s)')
    m = p.findall(last)
    if len(m) > 0:

        eta = m[0]
        print eta

