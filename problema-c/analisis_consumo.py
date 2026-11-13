"""
Laboratorio 5 - Problema C
Analisis del registro de corriente (Actividades 2 a 6).

Lee un CSV con las columnas que pide la consigna:

    tiempo_s, v_shunt_V, corriente_mA, estado

- tiempo_s:     tiempo de cada muestra, en segundos
- v_shunt_V:    tension medida sobre la resistencia shunt, en voltios
- corriente_mA: corriente en mA. Si se deja vacia, se calcula como
                I = Vshunt / Rshunt
- estado:       ACTIVO, STANDBY o APAGADO (el estado del micro en esa muestra)

Uso:
    python analisis_consumo.py mediciones.csv

Genera:
    corriente_vs_tiempo.png   grafica de corriente contra tiempo
    promedio_por_estado.png   comparacion de corrientes promedio
    y muestra por pantalla la tabla comparativa, la carga, la potencia,
    la autonomia y la reduccion porcentual.
"""

import csv
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------
# Datos del montaje: COMPLETAR con los valores reales
# ----------------------------------------------------------------------
R_SHUNT_OHM = 0.1          # resistencia shunt
VCC_V = 5.0                # tension de alimentacion medida
BATERIA_MAH = 1200.0       # capacidad nominal de la bateria elegida
ESTADO_REFERENCIA = "ACTIVO"   # contra que estado se calcula la reduccion


def leer(archivo):
    muestras = []
    with open(archivo, newline="", encoding="utf-8-sig") as f:
        for fila in csv.DictReader(f):
            if not (fila.get("tiempo_s") or "").strip():
                continue
            t = float(fila["tiempo_s"].replace(",", "."))
            v = (fila.get("v_shunt_V") or "").strip().replace(",", ".")
            i = (fila.get("corriente_mA") or "").strip().replace(",", ".")
            if i:
                corriente = float(i)
            else:
                corriente = float(v) / R_SHUNT_OHM * 1000.0     # I = Vshunt / Rshunt
            muestras.append((t, corriente, (fila.get("estado") or "").strip().upper()))
    muestras.sort()
    return muestras


def por_estado(muestras):
    """Junta las muestras de cada estado. La carga se integra por trapecios,
    asi el promedio queda ponderado por el tiempo aunque el muestreo no sea
    parejo."""
    res = {}
    for k in range(len(muestras)):
        t, i, e = muestras[k]
        d = res.setdefault(e, {"min": i, "max": i, "carga_mAs": 0.0, "tiempo_s": 0.0, "n": 0})
        d["min"] = min(d["min"], i)
        d["max"] = max(d["max"], i)
        d["n"] += 1
        if k > 0 and muestras[k - 1][2] == e:
            t0, i0, _ = muestras[k - 1]
            d["carga_mAs"] += (i + i0) / 2.0 * (t - t0)        # Q = integral de I dt
            d["tiempo_s"] += t - t0
    for d in res.values():
        d["prom"] = d["carga_mAs"] / d["tiempo_s"] if d["tiempo_s"] > 0 else (d["min"] + d["max"]) / 2.0
    return res


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    muestras = leer(sys.argv[1])
    if len(muestras) < 2:
        print("El archivo no tiene muestras suficientes.")
        return

    res = por_estado(muestras)

    print(f"\nArchivo: {sys.argv[1]}   muestras: {len(muestras)}")
    print(f"Rshunt = {R_SHUNT_OHM} ohm   Vcc = {VCC_V} V   Bateria = {BATERIA_MAH} mAh\n")
    print(f"{'Estado':<10}{'Imin mA':>10}{'Imax mA':>10}{'Iprom mA':>10}{'t (s)':>9}"
          f"{'Q (mAh)':>11}{'P (mW)':>9}{'Autonomia ideal':>18}")
    for e, d in res.items():
        q_mah = d["carga_mAs"] / 3600.0
        p_mw = VCC_V * d["prom"]                               # P = Vcc * Iprom
        horas = BATERIA_MAH / d["prom"] if d["prom"] > 0 else float("inf")   # t = C / Iprom
        print(f"{e:<10}{d['min']:>10.3f}{d['max']:>10.3f}{d['prom']:>10.3f}{d['tiempo_s']:>9.1f}"
              f"{q_mah:>11.5f}{p_mw:>9.2f}{horas:>12.1f} h ({horas / 24:.1f} d)")

    # Promedio de todo el registro (ciclo completo)
    carga_total = sum(d["carga_mAs"] for d in res.values())
    tiempo_total = sum(d["tiempo_s"] for d in res.values())
    if tiempo_total > 0:
        i_total = carga_total / tiempo_total
        print(f"\nCiclo completo: Iprom = {i_total:.3f} mA   Q = {carga_total / 3600.0:.5f} mAh"
              f"   P = {VCC_V * i_total:.2f} mW   autonomia ideal = {BATERIA_MAH / i_total:.1f} h")

    # Reduccion porcentual respecto de la referencia
    if ESTADO_REFERENCIA in res:
        ref = res[ESTADO_REFERENCIA]["prom"]
        print(f"\nReduccion respecto de {ESTADO_REFERENCIA} ({ref:.3f} mA):")
        for e, d in res.items():
            if e != ESTADO_REFERENCIA and ref > 0:
                print(f"  {e:<10} {(ref - d['prom']) / ref * 100.0:6.1f} %")

    # ---- Grafica de corriente contra tiempo ----
    colores = {"ACTIVO": "tab:red", "STANDBY": "tab:orange", "APAGADO": "tab:blue"}
    plt.figure(figsize=(10, 4.5))
    inicio = 0
    for k in range(1, len(muestras) + 1):
        if k == len(muestras) or muestras[k][2] != muestras[inicio][2]:
            tramo = muestras[inicio:k + 1] if k < len(muestras) else muestras[inicio:k]
            e = muestras[inicio][2]
            plt.plot([m[0] for m in tramo], [m[1] for m in tramo],
                     color=colores.get(e, "gray"), label=e)
            inicio = k
    manijas, etiquetas = plt.gca().get_legend_handles_labels()
    unicos = dict(zip(etiquetas, manijas))
    plt.legend(unicos.values(), unicos.keys())
    corrientes = [m[1] for m in muestras if m[1] > 0]
    if corrientes and max(corrientes) / min(corrientes) > 100:
        plt.yscale("log")                                      # varios ordenes de magnitud
    plt.title("Corriente de alimentacion en funcion del tiempo")
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Corriente (mA)")
    plt.grid(True, which="both", alpha=0.3)
    plt.tight_layout()
    plt.savefig("corriente_vs_tiempo.png", dpi=150)

    # ---- Comparacion de promedios ----
    plt.figure(figsize=(6, 4))
    nombres = list(res.keys())
    valores = [res[e]["prom"] for e in nombres]
    barras = plt.bar(nombres, valores, color=[colores.get(e, "gray") for e in nombres])
    for b, v in zip(barras, valores):
        plt.text(b.get_x() + b.get_width() / 2, v, f"{v:.2f}", ha="center", va="bottom")
    if valores and min(valores) > 0 and max(valores) / min(valores) > 100:
        plt.yscale("log")
    plt.title("Corriente promedio por estado")
    plt.ylabel("Corriente promedio (mA)")
    plt.tight_layout()
    plt.savefig("promedio_por_estado.png", dpi=150)

    print("\nGraficas guardadas: corriente_vs_tiempo.png y promedio_por_estado.png")


if __name__ == "__main__":
    main()
