import ini  
devices = ini.read_devices()
deviceIn = devices[0]
deviceOut = devices[1]

import numpy as np
import sounddevice as sd
from scipy.signal import remez, lfilter
import win32api
import win32con

# --- CONFIG ---
FS = 48000              # campionamento VAC
# F0 = 1500.0             # pivot inversione (Hz) ~ metà banda audio
F0 = -1500.0             # pivot 0
NUMTAPS = 129           # dispari; più alto = più pulito, più latenza
BLOCK = 1024            # buffer callback

# --- Hilbert transformer FIR (Type-III) ---
# Banda passante normalizzata (0..1) dove 1 = Nyquist
# Evita troppo vicino a 0 e Nyquist per stabilità/attenuazione
bands = [0.02, 0.48]
h_hilb = remez(NUMTAPS, bands, [1], type='hilbert', fs=1.0)

# Ritardo gruppo per allineare parte reale con la parte Hilbert
delay = (NUMTAPS - 1) // 2
delay_line = np.zeros(delay, dtype=np.float32)

# Stato filtro Hilbert
zi = np.zeros(NUMTAPS - 1, dtype=np.float32)

# Oscillatore complesso per shift
phase = 0.0
w = 2.0 * np.pi * F0 / FS

def process_block(x: np.ndarray) -> np.ndarray:
    global zi, delay_line, phase

    x = x.astype(np.float32, copy=False)

    # Hilbert(x) streaming
    xh, zi = lfilter(h_hilb, [1.0], x, zi=zi)

    # Allineamento: ritarda il reale di 'delay' campioni
    x_del = np.concatenate([delay_line, x])[:len(x)]
    delay_line = np.concatenate([delay_line, x])[len(x):]

    # Analitico
    xa = x_del + 1j * xh

    # Vettore esponenziale per shift
    n = np.arange(len(x), dtype=np.float32)
    exp_neg = np.exp(-1j * (phase + w * n))
    exp_pos = np.conj(exp_neg)  # e^{+j...}

    # Inversione spettrale attorno a f0: shift down, conj, shift up
    y = np.real(np.conj(xa * exp_neg) * exp_pos).astype(np.float32)

    # Aggiorna fase (mantieni continuità tra blocchi)
    phase = (phase + w * len(x)) % (2.0 * np.pi)
    return y

def callback(indata, outdata, frames, time, status):
    if status:
        # puoi loggare se vuoi; qui non stampo per non glitchare audio
        pass

    x = indata[:, 0]  # mono
    y = process_block(x)

    outdata[:, 0] = y

def main():
    # Seleziona device VAC a mano qui (nome o indice)
    # Esempio: device=(in_idx, out_idx)
    # Se lasci None usa default.

    try:
        with sd.Stream(
            samplerate=FS,
            blocksize=BLOCK,
            dtype='float32',
            channels=1,
            callback=callback,
            device=devices,
            latency='low',
        ):
            print(f"Running: FS={FS}Hz, F0={F0}Hz, taps={NUMTAPS}, block={BLOCK}")
            print("CTRL+C per uscire.")
            while True:
                sd.sleep(1000)
    except Exception as e:
        print(e)
        win32api.MessageBox(0, "Controlla che i dispositivi audio siano corretti e disponibili.", "Errore Stream",
                            win32con.MB_OK | win32con.MB_ICONERROR)
        
if __name__ == "__main__":
    main()
