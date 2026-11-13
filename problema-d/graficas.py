"""
Laboratorio 5 - Problema D, Actividad 6
Graficas comparativas a partir de las tablas medidas.

COMPLETAR los diccionarios de abajo con los valores medidos en el laboratorio
(dejar None en lo que no se pudo medir: esa barra no se dibuja) y ejecutar:

    python graficas_D.py

Genera un PNG por cada grafica que pide la consigna.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# 1. Consumo promedio (mA) frente al modo Sleep  -> programa "Prueba sleep y despertar"
consumo_por_modo = {
    "Sin dormir": None,
    "Idle": None,
    "ADC Noise Reduction": None,
    "Power-Down": None,
}

# 2. Consumo promedio (mA) frente a la configuracion de perifericos (PRR_MASCARA)
consumo_por_perifericos = {
    "Todos prendidos (0x00)": None,
    "Sin ADC (0x01)": None,
    "Sin USART0 (0x02)": None,
    "Sin SPI (0x04)": None,
    "Sin Timer1 (0x08)": None,
    "Sin Timer0 (0x20)": None,
    "Sin Timer2 (0x40)": None,
    "Sin TWI (0x80)": None,
    "Todos apagados (0xEF)": None,
}

# 3. Tiempo de despertar promedio (microsegundos) frente al modo Sleep
despertar_por_modo = {
    "Idle": None,
    "ADC Noise Reduction": None,
    "Power-Down": None,
}

# 4. Consumo en estado activo (mA) frente a la frecuencia de reloj -> "Prueba frecuencia de reloj"
consumo_por_frecuencia = {
    "16 MHz": None,
    "8 MHz": None,
    "2 MHz": None,
    "250 kHz": None,
    "125 kHz": None,
}

# 5. Consumo (mA) con y sin las optimizaciones de bajo consumo -> firmware del Problema B
consumo_optimizaciones = {
    "Sin optimizar (ACTIVO)": None,
    "Con Idle (STANDBY)": None,
    "Con Power-Down + PRR + WDT": None,
    "Con Power-Down + PRR sin WDT": None,
}


def barras(datos, titulo, eje_y, archivo):
    nombres = [k for k, v in datos.items() if v is not None]
    valores = [datos[k] for k in nombres]
    if not valores:
        print(f"{archivo}: sin datos, no se genera")
        return

    plt.figure(figsize=(8, 4.5))
    dibujo = plt.bar(nombres, valores, color="tab:green")
    for b, v in zip(dibujo, valores):
        plt.text(b.get_x() + b.get_width() / 2, v, f"{v:g}", ha="center", va="bottom")
    if min(valores) > 0 and max(valores) / min(valores) > 100:
        plt.yscale("log")           # escala logaritmica si hay varios ordenes de magnitud
        eje_y += " (escala logaritmica)"
    plt.title(titulo)
    plt.ylabel(eje_y)
    plt.xticks(rotation=25, ha="right")
    plt.grid(True, axis="y", which="both", alpha=0.3)
    plt.tight_layout()
    plt.savefig(archivo, dpi=150)
    plt.close()
    print(f"{archivo}: listo")


barras(consumo_por_modo, "Consumo promedio frente al modo Sleep", "Corriente (mA)", "D1_consumo_por_modo.png")
barras(consumo_por_perifericos, "Consumo frente a la configuracion de perifericos", "Corriente (mA)", "D2_consumo_por_perifericos.png")
barras(despertar_por_modo, "Tiempo de despertar frente al modo Sleep", "Tiempo (us)", "D3_tiempo_de_despertar.png")
barras(consumo_por_frecuencia, "Consumo en activo frente a la frecuencia de reloj", "Corriente (mA)", "D4_consumo_por_frecuencia.png")
barras(consumo_optimizaciones, "Consumo con y sin optimizaciones de bajo consumo", "Corriente (mA)", "D5_optimizaciones.png")
