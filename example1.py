def example(x):
    if x > 0:
        print("x is positive")
        if x % 2 == 0:
            print("x is even")
            if x > 100:
                print("x is large and even")
            else:
                if x == 2:
                    print("x is exactly two")
                else:
                    print("x is small and even")
        else:
            print("x is odd")
            if x < 10:
                print("x is a small odd number")
    else:
        print("x is not positive")
        if x == 0:
            print("x is zero")
        else:
            if x < -100:
                print("x is very negative")
            else:
                print("x is slightly negative")
    print("done")
