n = 2
x = 5
last_degree = 3
last_num = 5
n_sum = x


for i in range(1, n):
    n_sum -= (x**last_degree)/last_num
    last_degree += 2
    last_num += 2

print(int(n_sum))
