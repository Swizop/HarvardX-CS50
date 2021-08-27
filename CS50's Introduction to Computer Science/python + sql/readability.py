def regulatrei(a,b):
    x= 100*a/b
    return x
text=str(input("Your text here: "))
letters=words=prop=0
for i in range(len(text)):
    if text[i].lower()>='a' and text[i].lower()<='z':
        letters+=1
    elif text[i]=='!' or text[i]=='.' or text[i]=='?':
        prop+=1
    elif text[i]==' ':
        words+=1
words+=1
CL=0.0588 * regulatrei(letters,words) - 0.296 * regulatrei(prop,words) - 15.8
if (int(CL*10))%10>=5:
    ans=int(CL+1)
else:
    ans=int(CL)
if ans<1:
    print("Before Grade 1")
elif ans>=16:
    print("Grade 16+")
else:
    print(f"Grade {ans}")