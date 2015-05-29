import urllib

uf = urllib.urlopen('http://localhost:8080/data.json')  # this is where the dump1090 data is stored
w = open("data.dat", 'a')

for line in uf.read():  # read source code
    w.write(line)

w.close()
