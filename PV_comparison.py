import math
import matplotlib.pyplot as plt

# =========================
# 1) Grundlegende Annahmen
# =========================
r = 0.0412           # Kalkulationszinssatz (4,12 %)
n = 30               # Betrachtungszeitraum in Jahren
base_cost_y1 = 2247  # Stromkosten im Jahr 1 ohne PV (ca. 2.247 €)
growth = 0.03        # Jährliche Strompreissteigerung (3 %)

# Angebotspreise
cost_offer1 = 23364
cost_offer2 = 32325
cost_offer3 = 25850

# =========================
# 2) Funktionen zur Berechnung
# =========================

def stromkosten_ohne_pv(i):
    """
    Stromkosten im Jahr i ohne PV-Anlage,
    basierend auf base_cost_y1 und growth=3%.
    """
    return base_cost_y1 * ((1 + growth)**(i - 1))

# Angebot 1 & 3: 30 % Netzbezug zum normalen (wachsenden) Tarif
def stromkosten_mit_pv_1_3(i):
    return 0.30 * stromkosten_ohne_pv(i)

# Angebot 2: 30 % Netzbezug zum fixen Tarif 12 ct/kWh (ca. 334,8 €/Jahr)
def stromkosten_mit_pv_2(i):
    return 334.8

def npv_berechnen(kaufpreis, cost_pv_func):
    """
    Berechnet den NPV (Netto-Barwert) über 30 Jahre:
    NPV = -kaufpreis + Summe( (Stromkosten ohne - Stromkosten mit) / (1+r)^i ).
    """
    npv = -kaufpreis
    for i in range(1, n+1):
        cost_ohne = stromkosten_ohne_pv(i)
        cost_mit  = cost_pv_func(i)
        einsparung = cost_ohne - cost_mit
        # Diskontieren mit (1+r)^i
        npv += einsparung / ((1 + r)**i)
    return npv

def npv_kumulativ_pro_jahr(kaufpreis, cost_pv_func):
    """
    Liefert eine Liste, die für jedes Jahr i (1..n) den
    'kumulierten Barwert' (partial NPV) bis einschließlich Jahr i enthält.
    
    partial_NPV(i) = 
        -kaufpreis 
        + Summe_{j=1..i} [ (Stromkosten ohne - Stromkosten mit) / (1+r)^j ]
    """
    werte = []
    sum_disc = 0.0
    for i in range(1, n+1):
        cost_ohne = stromkosten_ohne_pv(i)
        cost_mit  = cost_pv_func(i)
        einsparung = cost_ohne - cost_mit
        # diskontierte Einsparung für Jahr i
        disc_einsparung = einsparung / ((1 + r)**i)
        sum_disc += disc_einsparung
        werte.append( sum_disc - kaufpreis )
    return werte

# =========================
# 3) NPV für alle Angebote
# =========================

npv1 = npv_berechnen(cost_offer1, stromkosten_mit_pv_1_3)
npv2 = npv_berechnen(cost_offer2, stromkosten_mit_pv_2)
npv3 = npv_berechnen(cost_offer3, stromkosten_mit_pv_1_3)

print("Finaler NPV (30 Jahre) für Angebot 1:", round(npv1, 2), "€")
print("Finaler NPV (30 Jahre) für Angebot 2:", round(npv2, 2), "€")
print("Finaler NPV (30 Jahre) für Angebot 3:", round(npv3, 2), "€")

# Kumulierte (partial) NPVs pro Jahr
pn1 = npv_kumulativ_pro_jahr(cost_offer1, stromkosten_mit_pv_1_3)
pn2 = npv_kumulativ_pro_jahr(cost_offer2, stromkosten_mit_pv_2)
pn3 = npv_kumulativ_pro_jahr(cost_offer3, stromkosten_mit_pv_1_3)

# =========================
# 4) Diagramme
# =========================

# -- Plot A: Verlauf des kumulierten Barwerts über die Jahre --
plt.figure()  # eigener Figure-Canvas
xwerte = range(1, n+1)

plt.plot(xwerte, pn1, label="Angebot 1")
plt.plot(xwerte, pn2, label="Angebot 2")
plt.plot(xwerte, pn3, label="Angebot 3")

plt.xlabel("Jahr")
plt.ylabel("Kumulierter Barwert (Euro)")
plt.title("Entwicklung des (teilweisen) Barwerts über 30 Jahre")
plt.legend()
plt.grid(True)
plt.show()

# -- Plot B: Balkendiagramm Endwerte (finaler NPV nach 30 Jahren) --
plt.figure()  # eigener Figure-Canvas

endwerte = [npv1, npv2, npv3]
labels   = ["Angebot 1", "Angebot 2", "Angebot 3"]

plt.bar(labels, endwerte)
plt.xlabel("Angebot")
plt.ylabel("Netto-Barwert nach 30 Jahren (Euro)")
plt.title("Vergleich finaler Barwerte")
plt.grid(True, axis="y")
plt.show()
