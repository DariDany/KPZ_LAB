def square(x):
    def multiply(y):
        return y * y
    return multiply(x)


result = square(4)
print(result)
