import numpy as np

from constants import TRAIN_BARS, SUBDIVISIONS, MIDI_NOTES, PARAM_SIZE, LAYER_SIZES
from model import Autoencoder
from sample import Sample

mode = "VG_Music"

weights_path = "data/model/" + mode + ".h5"
latent_path = "data/model/" + mode + ".npy"

class MusicGenerator:
    def __init__(self):
        self.ae = Autoencoder((TRAIN_BARS, SUBDIVISIONS*4, MIDI_NOTES), PARAM_SIZE, LAYER_SIZES)
        self.ae.load_weights(weights_path)
        self.ae.compile(0.0015)
        self._pca()

    def map_normal(self, samples):
        return self.means + self.stds * np.dot(samples * self.e_vals, self.e_vecs)

    def make_random_songs(self, n, savepath="testsongs/"):
        latent = np.random.normal(size=(n, PARAM_SIZE))
        samples = self.ae.decoder.predict(self.map_normal(latent))
        self.save_songs(samples, savepath=savepath)

    def make_songs(self, samples, thresh, ids, savepath="testsongs/"):
        samples = self.ae.decoder.predict(self.map_normal(samples))
        self.save_songs(samples, ids=ids, thresh=thresh, savepath=savepath)

    def get_note_array(self, sample):
        s = self.ae.decoder.predict(self.map_normal(sample))
        return s.reshape(TRAIN_BARS * 4 * SUBDIVISIONS, MIDI_NOTES)
    
    @staticmethod
    def save_songs(samples, ids=None, thresh=0.5, savepath="testsongs/"):
        if ids is None:
            ids = list(range(len(samples)))
        if isinstance(thresh, float):
            thresh = [thresh for i in range(len(samples))]
        for i, s in enumerate(samples):
            Sample(s.reshape(TRAIN_BARS * 4 * SUBDIVISIONS, MIDI_NOTES).T).save_midi(savepath + str(ids[i]) + ".midi", thresh=thresh[i])

    def _pca(self):
        latent_space = np.load(latent_path)
        self.means = np.mean(latent_space, axis=0)
        self.stds = np.std(latent_space, axis=0)
        normalised_space = (latent_space - self.means) / self.stds
        normalised_cov = np.cov(normalised_space.T)
        self.e_vals, self.e_vecs = np.linalg.eig(normalised_cov)


if __name__ == "__main__":
    test = MusicGenerator()
    test.make_random_songs(20)
