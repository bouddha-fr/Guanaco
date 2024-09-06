pass_str = "70,65,85,88,32,80,65,83,83,87,79,82,68,32,72,65,72,65"
tab2 = pass_str.split(',')
mot_de_passe = ''.join([chr(int(c)) for c in tab2])
print(mot_de_passe)