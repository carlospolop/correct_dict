# -*- coding: utf-8 -*-

#MEJORAS
#QUE LA CREACION DE PATRONSES SEA RECURRENTE, ES DECIR, QUE SE PUEDAN CREAR COMBINACIONES DE MAS DE 2 caracteres
#QUE DETECTE SI ES UN DICCIONARIO MUY ESPECIFICO (es decir, si solo usa combinaciones de 8xxxxxxxx, que solo se hagan patrones para ello)

from datetime import datetime, date, time, timedelta
import calendar
import re
#import os
import sys

if(len(sys.argv) < 2):
    print "Debe indicar el nombre del diccionario"
    print "sintaxis: "+sys.argv[0]+" <path del diccionario>"
    sys.exit(0)

#Cadena = String del que eliminar caracteres
#Reemplazo = Caracteres a eliminar (caracter:"")
def rm_noVisibles(cadena):
    #"""Reemplazo múltiple de cadenas en Python."""
    reemplazo = {"\r":"", "\n":""}
    regex = re.compile("(%s)" % "|".join(map(re.escape, reemplazo.keys())))
    return regex.sub(lambda x: str(reemplazo[x.string[x.start() :x.end()]]), cadena)
#Recibe un array de la palabras y las deja listas para ser escritas
def arregla(palabras_distintas):
    arregladas = []
    for palabra in palabras_distintas:
        arregladas.append(rm_noVisibles(palabra)+"\n")
    return arregladas

#Saca info del diccionario dado leyendolo una vez:
#Numero de palabras empezando por minusculas
#Numero de palabras empezando por mayusculas
#Numero de palabras empezando por numeros
#Numero de palabras empezando por simbolos
def info_dic(diccionario, buffersize):#periodo):
    print "Obteniendo info..."
    global patron_simple_minus
    global patron_simple_mayus
    global patron_simple_num
    global patron_simple_sim
    minus = re.compile(patron_simple_minus)
    mayus = re.compile(patron_simple_mayus)
    num = re.compile(patron_simple_num)
    sim = re.compile(patron_simple_sim)
    minus_cont = 0
    mayus_cont = 0
    num_cont = 0
    sim_cont = 0
#Cuenta el numero de lineas del diccionario
    #iterlen = lambda it: sum(1 for _ in it)
    #num_lineas = iterlen(file(diccionario))
    #ciclos = num_lineas / periodo
    #num_last_lines = num_lineas % periodo
    palabras_long_1 = []
    max_cont = 1000000

    last_palabra = ""
    f = open(diccionario, "r")
    buff = f.read(buffersize)
    print "Leyendo el diccionario"
    while len(buff):
        palabras = re.split("\n",buff)
        palabras[0] = last_palabra + palabras[0]
        last_palabra = palabras.pop()
        for palabra in palabras:
            if ((minus_cont < max_cont) and minus.match(palabra)):
                minus_cont += 1
            elif ((mayus_cont < max_cont) and num.match(palabra)):
                num_cont += 1
            elif ((num_cont < max_cont) and mayus.match(palabra)):
                mayus_cont += 1
            else:
                if (sim_cont < max_cont):
                    sim_cont += 1
            if ((len(palabra) == 1) and (not palabra in palabras_long_1)):
                palabras_long_1.append(palabra)
        buff = f.read(buffersize)
    f.close()
    total = minus_cont + num_cont + mayus_cont + sim_cont
    info_dic = [minus_cont, mayus_cont, num_cont, sim_cont, palabras_long_1, total]#, num_lineas, ciclos, num_last_lines]
    print "Número total de palabras: "+ str(total)
    print "Número de palabras empezando con minúsculas: "   +str(minus_cont)
    print "Número de palabras empezando con mayúsculas: "   +str(mayus_cont)
    print "Número de palabras empezando con números: "      +str(num_cont)
    print "Número de palabras empezando con símbolos: "     +str(sim_cont)
    print ""
    return info_dic

#Determina los patrones a usar en base a la info obtenida
def determinaPatron(patron, cont, is_patron_sec):
    cota = 1000 * 26 #Maximo tamaño medio de array que queremos permitir -- cota_num = 10 * cota; cota_letras = 26 * cota
    mult = 1 if is_patron_sec else 3
    cota_fin = cota * mult
    for i in range(len(patron)-1,-1,-1):#vamos del len-1 al 0, de -1 en -1
        if cont > cota_fin*i:
            return patron[i]
    return patron[0] if is_patron_sec else [] #En caso de que cont == 0

#Genera un nuevo patron en base a los anteriores, sirve para mezclar letras y numeros
#o solo letras añadiendo generalizaciones de numeros y símbolos (para no olvidadar casos de le+anum o letra+sim)
def crea_patron_letras(patron_base,patron_sec_minus,patron_sec_mayus,patron_sec_num,aisla_numeros):
    global patron_simple_num_sim
    global patron_simple_sim
    patron_nuevo = []
    for patron1 in patron_base:
        for patron_sec_min in patron_sec_minus: #Combinamos con minusculas
            patron_nuevo.append(patron1+patron_sec_min)
        for patron_sec_may in patron_sec_mayus: #Combinamos con mayusculas
            patron_nuevo.append(patron1+patron_sec_may)
        if not aisla_numeros:
            for patron_sec_n in patron_sec_num: #Combinamos con numeros
                patron_nuevo.append(patron1+patron_sec_n)
            patron_nuevo.append(patron1+patron_simple_sim)
#Si se han añadido patrones no hay que olvidar las combinaciones de letras con numeros o simbolos:
    if aisla_numeros and (len(patron_nuevo) >= len(patron_base)):
        for patron1 in patron_base:
            patron_nuevo.append(patron1+patron_simple_num_sim)
    if patron_nuevo == []:
        patron_nuevo = patron_base
    return patron_nuevo

#Combina el patron base de los numeros con el patron sec de los num y con el de las letras (si no hay aislaminto)
def crea_patron_numeros(patron_base_num,patron_sec_minus,patron_sec_mayus,patron_sec_num,aisla_numeros):
    global patron_simple_letras_sim
    global patron_simple_sim
    patron_nuevo = []
    for patron1 in patron_base_num:
        for patron_sec_n in patron_sec_num:
            patron_nuevo.append(patron1+patron_sec_n)
        if not aisla_numeros:
            for patron_sec_min in patron_sec_minus:
                patron_nuevo.append(patron1+patron_sec_min)
            for patron_sec_may in patron_sec_mayus:
                patron_nuevo.append(patron1+patron_sec_may)
            patron_nuevo.append(patron1+patron_simple_sim)
#Si hemos combinado los patrones base y sec de numeros creando más patrones que los iniciales, hay que ñadir los caso de numero+letra
    if aisla_numeros and (len(patron_nuevo) >= len(patron_base_num)):
        for patron1 in patron_base_num:
            patron_nuevo.append(patron1+patron_simple_letras_sim)
    if patron_nuevo == []:
        patron_nuevo = patron_base_num
    return patron_nuevo

#Dado un patron recorre todo el archivo guardando en un array aquellas palabras que comienzan por dicho patron
# y no se repiten, luego llama al metodo para escribirlas
def recorre_diccionario(patron, diccionario, buffersize): #num_lineas, ciclos, num_last_lines, periodo):
    global palabras_repetidas
    f = open(diccionario, "r")
    palabras_distintas = []
    last_palabra = ""

    buff = f.read(buffersize)
    #print "Leyendo el diccionario"
    while len(buff): #Como vamos a cachos las ultima palabra siempre estará partida por lo general
        palabras = re.split("\n",buff)
        palabras[0] = last_palabra + palabras[0]
        last_palabra = palabras.pop()
        for palabra in palabras:
            if (patron.match(palabra)):
                if (not (palabra in palabras_distintas)): #match devuelve None si el patron no esta al inicio de la palabra
                    palabras_distintas.append(palabra)
                else:
                    palabras_repetidas.append(palabra)
        buff = f.read(buffersize)
    f.close()
    return palabras_distintas

#Dado un array escribe todas las palabras en un archivo sin repetirlas
def escribe_diccionario(palabras_distintas, diccionario_nuevo):
    global numero_palabras
    palabras_distintas.sort()
    with open(diccionario_nuevo, 'a') as file:
        file.writelines(arregla(palabras_distintas))
    numero_palabras += len(palabras_distintas)
    #VERBOSE
    print "Reescritas "+str(len(palabras_distintas))+" palabras - "+str(numero_palabras)
    print ""


#########
#DEFINICION DE CONSTANTES
###########
comienzo = datetime.now()
diccionario = sys.argv[1]
array_dic = re.split("/",diccionario)
ppal_str_dic = array_dic[len(array_dic)-1]
diccionario_nuevo = "Dic_corregido"+ str(comienzo.date())+"_"+str(comienzo.hour)+":"+str(comienzo.minute)+"_"+ppal_str_dic
#dic_weight = os.path.getsize(diccionario) #Esta en Bytes import os
numero_palabras = 0
aisla_numeros = True
#Patrones para crear los patrones finales
patron_num = [["[\d]"],
            ["[0-4]","[5-9]"],
            ["[0-2]","[3-6]","[7-9]"],
            ["[0-2]","[3-4]","[5-6]","[7-9]"],
            ["[01]","[23]","[45]","[67]","[89]"],
            ["0","1","2","3","4","5","6","7","8","9"]
            ]
patron_minus = [["[a-z]"],
            ["[a-m]","[n-z]"],
            ["[a-i]","[j-q]","[r-z]"],
            ["[a-g]","[h-n]","[o-t]","[u-z]"],
            ["[a-d]","[e-h]","[i-l]","[m-p]","[q-t]","[u-z]"],
            ["[a-b]","[c-d]","[e-g]","[h-j]","[k-m]","[n-p]","[q-s]","[t-v]","[w-z]"],
            ["[ab]","[cd]","[ef]","[gh]","[i-k]","[lm]","[no]","[pq]","[r-t]","[u-w]","[xyz]"],
            ["[ab]","[cd]","[ef]","[gh]","[ij]","[kl]","[mn]","[op]","[qr]","[st]","[uvw]","[xyz]"],
            ["a","b","c","e","[df]","[gh]","i","[jk]","l","m","n","o","[pq]",
            "r","s","t","u","[vw]","[xyz]"],
            ["a","b","c","e","d","f","g","h","i","j","k","l","m","n","o","p","q",
            "r","s","t","u","[vw]","[xyz]"]
            ]
patron_mayus = [
            ["[A-Z]"],
            ["[A-M]","[N-Z]"],
            ["[A-I]","[J-Q]","[R-Z]"],
            ["[A-G]","[H-N]","[O-T]","[U-Z]"],
            ["[A-D]","[E-H]","[I-L]","[M-P]","[Q-T]","[U-Z]"],
            ["[A-B]","[C-D]","[E-G]","[H-J]","[K-M]","[N-P]","[Q-S]","[T-V]","[W-Z]"],
            ["[AB]","[CD]","[EF]","[GH]","[I-K]","[LM]","[NO]","[PQ]","[R-T]","[U-W]","[XYZ]"],
            ["[AB]","[CD]","[EF]","[GH]","[IJ]","[KL]","[MN]","[OP]","[QR]","[ST]","[UVW]","[XYZ]"],
            ["A","B","C","E","[DF]","[GH]","I","[JK]","L","M","N","O","[PQ]",
            "R","S","T","U","[VW]","[XYZ]"],
            ["A","B","C","E","D","F","G","H","I","J","K","L","M","N","O","P","Q",
            "R","S","T","U","[VW]","[XYZ]"]
            ]
patron_sim = ["[\W_]"]
#Patrones para buscar correspondencia o para complementar
patron_simple_minus = "[a-z]"
patron_simple_mayus = "[A-Z]"
patron_simple_num = "[\d]"
patron_simple_sim = "[\W_]"
patron_simple_letras_sim = "[a-zA-Z\W_]"
patron_simple_num_sim = "[\W_\d]"

buffersize = 200000
#periodo = 500
palabras_repetidas = []
##############
#LOGICA DEL PROGRAMA
##############
#El flujo es el siguiente:
#   Creamos los patrones que usaremos para guardar las palabras poco a poco
#   Recorremos todos los posibles comienzos de las palabras del diccionario
#       En cada uno de esos recorridos buscamos las palabras que comiencen por el mismo patron y las guardamos en un array
#       Escribimos dicho array en el nuevo diccionario
#
info_dic_array = info_dic(diccionario, buffersize)#periodo)
minus_cont = info_dic_array[0]
mayus_cont = info_dic_array[1]
num_cont = info_dic_array[2]
sim_cont = info_dic_array[3]

is_patron_sec = False
patron_base_minus = determinaPatron(patron_minus, minus_cont, is_patron_sec)
patron_base_mayus = determinaPatron(patron_mayus, mayus_cont, is_patron_sec)
patron_base_num   = determinaPatron(patron_num, num_cont, is_patron_sec)
patron_base_sim   = determinaPatron(patron_sim, num_cont, is_patron_sec)

print "PATRON BASE MINUSCULAS: "+str(patron_base_minus)
print "PATRON BASE MAYUSCULAS: "+str(patron_base_mayus)
print "PATRON BASE NUMEROS: "+str(patron_base_num)
print "PATRON BASE SIMBOLOS: "+str(patron_base_sim)

is_patron_sec = True
patron_sec_minus = determinaPatron(patron_minus, minus_cont, is_patron_sec)
patron_sec_mayus = determinaPatron(patron_mayus, mayus_cont, is_patron_sec)
patron_sec_num   = determinaPatron(patron_num, num_cont, is_patron_sec)

print "PATRON SEC MINUSCULAS: "+str(patron_sec_minus)
print "PATRON SEC MAYUSCULAS: "+str(patron_sec_mayus)
print "PATRON SEC NUMEROS: "+str(patron_sec_num)

patron_minus = crea_patron_letras(patron_base_minus,patron_sec_minus,patron_sec_mayus,patron_sec_num,aisla_numeros)
patron_mayus = crea_patron_letras(patron_base_mayus,patron_sec_minus,patron_sec_mayus,patron_sec_num,aisla_numeros)
patron_num = crea_patron_numeros(patron_base_num,patron_sec_minus,patron_sec_mayus,patron_sec_num,aisla_numeros)

print "PATRON FINAL MINUSCULAS: "+str(patron_minus)
print "PATRON FINAL MAYUSCULAS: "+str(patron_mayus)
print "PATRON FINAL NUMEROS: "+str(patron_num)
print "PATRON FINAL SIMBOLOS: "+str(patron_sim)
print ""

patrones = patron_minus + patron_mayus + patron_num + patron_sim

palabras_long_1 = info_dic_array[4]
print "PALABRAS LONG 1: "+str(palabras_long_1)
escribe_diccionario(palabras_long_1, diccionario_nuevo)
for patron in patrones:
    #VERBOSE
    print "Usando el patron "+patron
    patron_compilado = re.compile(patron)
    palabras_distintas = recorre_diccionario(patron_compilado, diccionario, buffersize)#num_lineas, ciclos, num_last_lines, periodo)
    escribe_diccionario(palabras_distintas, diccionario_nuevo)

###########
##FIN DEL PROGRAMA
###########
fin = datetime.now()
tiempo_tardado = fin - comienzo
print("Se ha tardado: "+str(tiempo_tardado.seconds/60)+" minuto(s) "+str(tiempo_tardado.seconds%60)+" segundo(s)")
print "Número de palabras repetidas: "+str(info_dic_array[5]-numero_palabras)
print "PALABRAS REPETIDAS: "+str(palabras_repetidas)
