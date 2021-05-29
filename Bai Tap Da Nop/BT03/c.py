

b = 1
c = -4
print(c, bin(c))
c = (c & ~1) | (b & 1)
print(c, bin(c), int(bin(c),2))