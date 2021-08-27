def main():
    n=int(get_number()*100)
    if n==0:
        print(0)
        return
    v=[25,10,5,1]
    rest=0
    for i in v:
        rest=rest+int(n/i)
        n=n%i
    print(rest)
def get_number():
    while True:
        x=float(input("please state your change\n"))
        if x>=0:
            return x
main()