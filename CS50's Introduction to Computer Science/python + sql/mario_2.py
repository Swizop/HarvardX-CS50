def main():
    n=get_number()
    for i in range(1,n+1):
        j=1
        while j<=n-i:
            print(" ",end="")
            j+=1
        while j<=n:
            print("#",end="")
            j+=1
        print(" ",end="")
        j=1
        while j<=i:
            print("#",end="")
            j+=1
        while j<=n:
            print(" ",end="")
            j+=1
        if i<n :
            print()
def get_number():
    while True:
        x=int(input("provide a number from 1 to 8\n"))
        if x>0 and x<9:
            return x
main()
