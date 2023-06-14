import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication
import metodos


class index(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("vistaER_Generica.ui", self)
        self.botonIngresar.clicked.connect(self.ingresarDatos)

    def ingresarDatos(self):
        patron = self.lineaDeEntradaER.text()
        patronAdaptado = metodos.adaptarER(patron)
        cadena = self.lineaDeEntradaCadena.text()
        cadenaAdaptada = metodos.adaptarEntrada(cadena)

        expReg = metodos.ExpReg(patronAdaptado)
        validez = expReg.comparar(cadenaAdaptada)
        if validez:
            self.resultados.setText("Cadena Valida.")
        else:
            self.resultados.setText("Cadena Invalida.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    GUI = index()
    GUI.show()
    sys.exit(app.exec_())