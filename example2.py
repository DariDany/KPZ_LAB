sum = 0
for i in range(1, 6):
    for j in range(1, 4):
        sum += j
        k = 0
        while k < 2:
            sum += k
            k += 1
print(sum)
