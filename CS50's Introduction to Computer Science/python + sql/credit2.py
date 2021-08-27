import math
# def length(x):
#     if x==0:
#         l=1
#     else:
#         l=int(math.log10(x)+1)
#     return l
def legit_check(x):
    s1=s2=0
    while x>0:
        s1=s1+x%10
       # print(f"s1:{x%10} {x}")
        x=int(x/10)

        q=x%10*2
        p=0
        while q>0:
            p=p+q%10
            q=int(q/10)
        s2=s2+p
       # print(f"s2:{x%10*2} {x}")
        x=int(x/10)
    #print(s1,s2)
    if (s1+s2)%10==0:
        return 1
    return 0
def americane(x):
    card=str(x)
    if len(card)==15  and card[0]=='3' and (card[1]=='4' or card[1]=='7'):
        return 1
    return 0
def master(x):
    card=str(x)
    if len(card)==16  and card[0]=='5' and card[1]>'0' and card[1]<'6':
        return 1
    return 0
def visa(x):
    card=str(x)
    if (len(card)==13 or len(card)==16)  and card[0]=='4':
        return 1
    return 0
def main():
    card=int(input("your card number:\n"))
    if legit_check(card)==0:
        print("INVALID\n")
        return
    if americane(card)==1:
        print("AMEX\n")
        return
    if master(card)==1:
        print("MASTERCARD\n")
        return
    if visa(card)==1:
        print("VISA\n")
        return
    print("INVALID\n")
    return
main()

