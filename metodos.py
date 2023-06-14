import sys


def definirRango(inicio, fin):
    rango = ['(']
    for c in range(ord(inicio), ord(fin)):  # Donde ord, devuelve el unicodigo de un caracter introducido.
        rango.append(chr(c))
        rango.append('|')
    rango.append(fin)
    return rango


def definirCocatenacion(expresion: str) -> list:
    rango = []
    i = 0
    while i < len(expresion):
        if expresion[i] == '[':
            inicio = expresion[i + 1]
            fin = expresion[i + 3]
            rango += definirRango(inicio, fin)
            i += 4
        else:
            rango.append(expresion[i] if expresion[i] != ']' else ')')
            if expresion[i] in {'(', '|'}:
                i += 1;
                continue
            elif i < len(expresion) - 1:
                if expresion[i + 1] not in {'*', '?', '+', ')', '|', ']'}:
                    rango.append('.')
            i += 1
    return rango


operadoresDePrecedencia = {
    '|': 0,  # Union +
    '.': 1,  # Concatenacion ()()
    '?': 2,  # Epsilon o Mas ^*
    '*': 2,  # Terminacion $
    '+': 2  # Uno o Mas ^+
}


def validarER(expresion: list) -> str:
    rango, pila = [], []
    for simbolos in expresion:
        if simbolos == '(':
            pila.append(simbolos)
        elif simbolos == ')':
            try:
                while pila[-1] != '(':
                    rango.append(pila.pop())
            except IndexError:
                sys.stderr.write("Expresion regular invalida, vuelva a correr el programa.\n")
                sys.exit(64)  # Terminar el programa
            else:
                pila.pop()  # Se le hace pop a (
        elif simbolos in {'+', '*', '?', '.', '|'}:
            while len(pila) > 0:
                if pila[-1] == '(':
                    break
                elif operadoresDePrecedencia[simbolos] > operadoresDePrecedencia[pila[-1]]:
                    break
                else:
                    rango.append(pila.pop())
            pila.append(simbolos)
        else:
            rango.append(simbolos)
    while len(pila) > 0:
        rango.append(pila.pop())
    return "".join(rango)


class Estado:
    def __init__(self, esFin: bool):
        self.esFin = esFin
        self.transicion = {}
        self.transicionesEpsilon = []

    def agregarTransicionesEpsilon(self, hacia):
        self.transicionesEpsilon.append(hacia)

    def agregarTransicion(self, hacia, simbolo):
        self.transicion[simbolo] = hacia


class AFND:
    def __init__(self, inicio: Estado, fin: Estado):
        self.inicio = inicio
        self.fin = fin


def desdeEpsilon() -> AFND:
    inicio = Estado(False)
    fin = Estado(True)
    inicio.agregarTransicionesEpsilon(fin)
    return AFND(inicio, fin)


def desdeSimbolo(simbolo) -> AFND:
    inicio = Estado(False)
    fin = Estado(True)
    inicio.agregarTransicion(fin, simbolo)
    return AFND(inicio, fin)


def concatenar(primero: AFND, segundo: AFND) -> AFND:
    primero.fin.agregarTransicionesEpsilon(segundo.inicio)
    primero.fin.esFin = False
    return AFND(primero.inicio, segundo.fin)


def union(primero: AFND, segundo: AFND) -> AFND:
    inicio = Estado(False)
    inicio.agregarTransicionesEpsilon(primero.inicio)
    inicio.agregarTransicionesEpsilon(segundo.inicio)
    fin = Estado(True)
    primero.fin.agregarTransicionesEpsilon(fin)
    primero.fin.esFin = False
    segundo.fin.agregarTransicionesEpsilon(fin)
    segundo.fin.esFin = False
    return AFND(inicio, fin)


def terminacion(afnd: AFND) -> AFND:
    inicio = Estado(False)
    fin = Estado(True)
    inicio.agregarTransicionesEpsilon(afnd.inicio)
    inicio.agregarTransicionesEpsilon(fin)
    afnd.fin.agregarTransicionesEpsilon(afnd.inicio)
    afnd.fin.agregarTransicionesEpsilon(fin)
    afnd.fin.esFin = False
    return AFND(inicio, fin)


def uno_O_Mas(afnd: AFND) -> AFND:
    inicio = Estado(False)
    fin = Estado(True)
    inicio.agregarTransicionesEpsilon(afnd.inicio)
    afnd.fin.agregarTransicionesEpsilon(afnd.inicio)
    afnd.fin.agregarTransicionesEpsilon(fin)
    afnd.fin.esFin = False
    return AFND(inicio, fin)


def cero_O_Uno(afnd: AFND) -> AFND:
    inicio = Estado(False)
    fin = Estado(True)
    inicio.agregarTransicionesEpsilon(afnd.inicio)
    inicio.agregarTransicionesEpsilon(fin)
    afnd.fin.agregarTransicionesEpsilon(afnd.inicio)  # editado para 0 o mas, en vez de 0 o 1
    afnd.fin.agregarTransicionesEpsilon(fin)
    afnd.fin.esFin = False
    return AFND(inicio, fin)


def validarPatron(expresion_A_Evaluar: str) -> AFND:
    if expresion_A_Evaluar == '':
        return desdeEpsilon()
    pila = []  # pila de sub AFND, para evaluar cada fragmento.
    try:
        for simbolo in expresion_A_Evaluar:
            if simbolo == '*':
                pila.append(terminacion(pila.pop()))
            elif simbolo == '+':
                pila.append(uno_O_Mas(pila.pop()))
            elif simbolo == '?':
                pila.append(cero_O_Uno(pila.pop()))
            elif simbolo == '|':
                derecha = pila.pop()
                izquierda = pila.pop()
                pila.append(union(izquierda, derecha))
            elif simbolo == '.':
                derecha = pila.pop()
                izquierda = pila.pop()
                pila.append(concatenar(izquierda, derecha))
            else:
                pila.append(desdeSimbolo(simbolo))
    except IndexError:
        sys.stderr.write("Expresion regular invalida, vuelva a correr el programa.\n")
        sys.exit(64)  # Terminar el programa.
    else:
        return pila.pop()


def asignarSiguienteEstado(estado: Estado, siguientesEstados: list, visitados: list):
    if len(estado.transicionesEpsilon) > 0:
        for est in estado.transicionesEpsilon:
            if not est in visitados:
                visitados.append(est)
                asignarSiguienteEstado(est, siguientesEstados, visitados)
    else:
        siguientesEstados.append(estado)


def buscar(afnd: AFND, palabra: str) -> bool:
    actual = []
    asignarSiguienteEstado(afnd.inicio, actual, [])
    for simbolo in palabra:
        siguientesEstados = []
        for estado in actual:
            if simbolo in estado.transicion:
                asignarSiguienteEstado(estado.transicion[simbolo], siguientesEstados, [])
        actual = siguientesEstados
    for estado in actual:
        if estado.esFin:
            return True
    return False


def adaptarER(patron):
    patron = patron.replace("+", "|")
    patron = patron.replace("^*", "?")
    patron = patron.replace("^|", "+")
    patron = patron.replace("$", "*")
    salida = patron
    print(salida)
    return salida


def adaptarEntrada(patron):
    patron = patron.replace("+", "|")
    patron = patron.replace("^*", "?")
    patron = patron.replace("^|", "+")
    patron = patron.replace("$", "*")
    salida = patron
    print(salida)
    return salida


class ExpReg:
    def __init__(self, expresion: str):
        expresion = validarER(definirCocatenacion(expresion))
        self.afnd = validarPatron(expresion)

    def comparar(self, palabra: str) -> bool:
        return buscar(self.afnd, palabra)