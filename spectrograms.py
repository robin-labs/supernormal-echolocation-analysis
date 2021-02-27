import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.io import wavfile

def plot_spectrogram(filename):
    sample_rate, samples = wavfile.read(filename)
    fig, axes = plt.subplots(nrows=2, ncols=1)
    print(samples.shape)
    for idx in (0,1):
        ax = axes[idx]
        channel = np.clip(samples[:, idx], a_min=0, a_max=None)
        ax.specgram(channel, Fs=sample_rate, scale='dB', NFFT=1024, scale_by_freq=False)
        ax.set_ylim(ymin=0, ymax=6e3)
        ax.set_ylabel('Frequency (Hz)')
        ax.set_xlabel('Time (sec)')
    plt.show()

plot_spectrogram("./supernormal-echolocation-presentations/media/audio/stims/spherical_chirp_300cm_s20_c1_cd-1_matched_a45.wav")