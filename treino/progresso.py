import math

dic_faixas = {'Branca': 0, 'Azul': 1, 'Roxa': 2, 'Marrom': 3, 'Preta': 4 }

def calcular_classes_upgrade(n):
    d = 1.47
    k = 30/math.log(d)
    aulas = k*math.log(n + d)

    return round(aulas)