# 🌊 Simulazione di Riflessione d'Onda (Code Challenge)

Questo progetto implementa una simulazione fluidodinamica ottimizzata per la visualizzazione della riflessione di un'onda su uno schermo rigido. Il codice è stato ingegnerizzato con un focus specifico sulla massimizzazione delle performance computazionali e del throughput di rendering.

---

## 🧠 Modellizzazione Fisica: Metodo della Sorgente Immagine

Per simulare la riflessione senza dover risolvere numericamente complesse equazioni differenziali alle derivate parziali (PDE) sul confine, abbiamo adottato il **Metodo della Sorgente Immagine**:

*   **Geometria:** Data una sorgente reale nell'origine $(0,0)$ e un muro verticale a $x = 1.5$, la condizione al contorno di riflessione totale è soddisfatta posizionando una sorgente identica e coerente in posizione speculare rispetto allo schermo, ovvero a $(3,0)$.
*   **Interferenza:** Il campo risultante $u_{tot}$ è la sovrapposizione lineare dei due campi d'onda. Lungo la linea dello schermo, i due fronti d'onda si scontrano simulando perfettamente l'effetto di rimbalzo dell'energia verso l'interno dello stagno.
*   **Opacità:** Il campo per $x > 1.5$ viene forzato a zero tramite clipping booleano per rappresentare l'ombra geometrica dietro lo schermo rigido.

---

## ⚡ Architettura Prestazionale (Optimized for Speed)

Il superamento della sfida di velocità è garantito da una serie di ottimizzazioni a basso livello che riducono i tempi di calcolo e di scrittura su disco.

### 1. Vettorializzazione e Riduzione dell'Instruction Count
Invece di utilizzare cicli iterativi per i $62.500$ pixel della griglia, il codice sfrutta il calcolo vettoriale di **NumPy**:
*   **SIMD (Single Instruction, Multiple Data):** Le operazioni matematiche vengono delegate a librerie C altamente ottimizzate che processano intere matrici simultaneamente.
*   **Eliminazione delle divisioni:** Abbiamo pre-calcolato l'inverso della velocità ($v^{-1}$) per trasformare le divisioni nel loop temporale in moltiplicazioni, operazione intrinsecamente più rapida per l'ALU della CPU.

### 2. Gestione della Memoria e Precisione (`float32`)
Il codice forza l'utilizzo del tipo di dato `np.float32` invece del `float64` standard di Python:
*   **Bandwidth:** Riduce della metà il volume di dati scambiato tra la cache della CPU e la RAM.
*   **Pre-allocazione:** Abbiamo implementato la tecnica del **Buffer Reuse**. Invece di allocare nuova memoria a ogni frame tramite `np.zeros_like`, utilizziamo una matrice pre-allocata (`u_base`) e il metodo `.copy()`, riducendo drasticamente il tempo speso dal sistema operativo nella gestione del memory heap.

### 3. Pre-calcolo delle Componenti Statiche
Abbiamo isolato le parti della formula fisica che non variano nel tempo:
*   **Mappe di Attenuazione:** Il termine di decadimento geometrico $1/\sqrt{R}$ viene calcolato una sola volta all'avvio per entrambe le sorgenti.
*   **Coordinate:** Le matrici delle distanze euclidee sono calcolate una tantum, rimuovendo l'onere della radice quadrata dai 200 frame dell'animazione.

### 4. Ottimizzazione del Rendering (Matplotlib Pipe)
Il rendering grafico è solitamente il collo di bottiglia principale. Abbiamo rimosso questo limite tramite:
*   **Aggiornamento diretto (`set_data`):** Non viene ricreato l'oggetto grafico, ma vengono iniettati i nuovi dati grezzi nella struttura esistente.
*   **Blitting:** Viene aggiornata solo l'area dei pixel variabile, mantenendo statici assi, titoli e lo schermo nero (`axvline`).
*   **Interpolazione 'Nearest':** Disabilita l'antialiasing spaziale durante il rendering dei frame, eliminando calcoli di interpolazione superflui durante la creazione della GIF.

### 5. Configurazione del Writer
Il salvataggio è affidato al writer **Pillow** con il parametro `cache_frame_data=False`. Questo impedisce a Matplotlib di accumulare l'intera sequenza di frame in memoria prima del salvataggio, stabilizzando i tempi di esecuzione e prevenendo picchi di utilizzo della RAM.

---

![Simulazione Riflessione](riflessione.gif)

## 🚀 Specifiche Tecniche

| Parametro | Dettaglio |
| :--- | :--- |
| **Griglia** | $250 \times 250$ (discretizzazione spaziale) |
| **Tempo Ritardato** | $\tau = t - R \cdot v^{-1}$ |
| **Regolarizzazione** | `np.maximum(R, 0.1)` per evitare singolarità nell'origine |
| **Frame Rate** | 20 FPS (Sincronizzato con la fisica $\Delta t = 0.05$) |
| **Colormap** | `RdBu` (bilanciata per pattern di interferenza) |

---

## 🛠️ Requisiti
*   **Python 3.10+**
*   **NumPy:** Calcolo matriciale.
*   **Matplotlib:** Motore di animazione e rendering.
*   **Pillow:** Compressione e codifica GIF.
