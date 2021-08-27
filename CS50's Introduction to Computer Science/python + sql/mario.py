
def main():
    q=nr()
    for i in range(0,q):
        if q-i-1>0:
            for j in range(0,q-i-1):
                print(" ",end="")
            j+=1
            for j in range(j,q):
                print("#",end="")
            print()
        else:
            for j in range(q):
                print('#',end='')
def nr():
    while True:
        a=int(input("please give a number from 1 to 8\n"))
        if a>0 and a<9:
            return a
main()