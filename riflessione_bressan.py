import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# --- Parametri fisici fissati ---
L = 12
N = 250
x_screen = 1.5
omega = 4.0
gamma = 0.5
v = 1.0
inv_v = 1.0/v
dt = 0.05
n_frames = 200
u_base = np.zeros((N,N), dtype=np.float32)
# --- Setup Griglia e Distanze ---
coord = np.linspace(-L/2, L/2, N)
X,Y = np.meshgrid(coord, coord)

# R1: sorgente reale (0,0), R2: sorgente immaginaria (3,0)
R1 = np.sqrt(X*X + Y*Y).astype(np.float32)
R2 = np.sqrt((X - 3.0)*(X - 3.0) + Y*Y).astype(np.float32)
attenuazione1 = 1.0 / np.sqrt(np.maximum(R1, 0.1)).astype(np.float32)
attenuazione2 = 1.0 / np.sqrt(np.maximum(R2, 0.1)).astype(np.float32)
# Maschera per lo schermo, True dove l'onda non passa
mask_screen = X > x_screen


def calcola_onda(t,R, attenuazione):
    tau = t - R*inv_v
    u = u_base.copy() #ritorna un array come R pieno di 0
    m = tau > 0
    #formula ampiezza
    u[m] = attenuazione[m] * np.exp(-gamma * tau[m]) * np.sin(omega * tau[m])
    return u

# --- Setup grafico ---
fig, ax = plt.subplots(figsize=(6,6))
#inizializzo l'immagine (aggiornata da FuncAnimation)
im = ax.imshow(np.zeros((N, N)), extent=[-L/2, L/2, -L/2, L/2], 
               origin='lower', cmap='RdBu', vmin=-2, vmax=2, interpolation='nearest')

# Disegno lo schermo (fisso)
ax.axvline(x_screen, color='black', linewidth=4)
ax.set_title("Riflessione Onda da Schermo")
ax.axis('off')

# --- Funzione di Animazione ---
def update(i):
    t_attuale = i * dt
    # Somma delle due onde
    u_totale = calcola_onda(t_attuale, R1, attenuazione1) + calcola_onda(t_attuale, R2, attenuazione2)
    # Applichiamo il muro
    u_totale[mask_screen] = 0
    # Aggiorniamo solo i dati dei pixel (velocissimo)
    im.set_data(u_totale)
    return [im]

# Creazione animazione
# blit=True serve a rinfrescare solo le parti che cambiano
ani = FuncAnimation(fig, update, frames=n_frames, interval=50, blit=True, cache_frame_data=False)

# Salvataggio diretto in GIF
#print("Generazione riflessione.gif in corso...")
ani.save('riflessione_bressan.gif', writer='pillow', fps=20)
plt.close()
#print("Completato!")