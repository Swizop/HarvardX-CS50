import csv
def main():
    with open("9.txt",'r') as file_txt:
        dna = file_txt.read()     #citire fisier txt
        with open("large.csv",'r') as csv_data:
            csv_reader=csv.reader(csv_data)    #cititor fisier csv

            header=next(csv_reader)         #header primeste prima linie
            iterheader=iter(header)          #transformat in iterabil pentru a putea fi manipulat mai usor
            next(iterheader)              #trecut peste "nume" adica prima sectiune
            v=[]                         #lista goala in care vor fi trecute, pe rand, lungimile maxime ale fiecarei secvente din header
            for secv in iterheader:
                lgmax=lg=i=0
                while i < len(dna)-len(secv)+1:
                    if dna[i:i+len(secv)]==secv:          #dna[i:i+len(secv)] nu include dna[i+len(secv)]
                        lg+=1
                        i=i+len(secv)
                    else:
                        if lg>lgmax:
                            lgmax=lg
                        lg=0
                        i+=1
                if lg>lgmax:
                    lgmax=lg
                v.append(lgmax)
            #print(v)
            for j in csv_reader:             #se verifica daca numerele unei persoane sunt egale cu numerele din v
                iterj=iter(j)                   #j trece prin datele fiecarei persoane, adica prin fiecare linie incepand cu L2
                next(iterj)           #se trece peste campul de nume ca sa fie verificate doar valorile
                k=0
                ok=1
                for x in iterj:
                    if not(int(x)==v[k]):
                        ok=0
                    k+=1
                if ok==1:
                    print(j[0])            #j[0] este campul de nume
                    return
            print("No match")
            return
main()









