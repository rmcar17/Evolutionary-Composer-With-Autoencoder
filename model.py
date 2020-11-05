import os
import pickle

from tensorflow.keras import layers
from tensorflow.keras import backend as K

from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.utils import plot_model

from constants import TRAIN_BARS, SUBDIVISIONS, MIDI_NOTES
from callbacks import step_decay_schedule, CustomCallback

# Layer Sizes: 2200, 300, 1800

BN_M = 0.9
DO_RATE = 0.1

class Autoencoder():
    def __init__(self, input_dim, params, layer_sizes, training=True):
        self.input_dim = input_dim
        self.params = params
        self.training = training
        self.layer_sizes = layer_sizes
        self._build()

    def _build(self):
        encoder_input = layers.Input(shape=self.input_dim, name="encoder_input")

        x = encoder_input
        print(K.int_shape(x))

        x = layers.Reshape((TRAIN_BARS, SUBDIVISIONS * 4 * MIDI_NOTES))(x)
        print(K.int_shape(x))

        x = layers.TimeDistributed(layers.Dense(self.layer_sizes[0], activation="relu"))(x)
        print(K.int_shape(x))

        x = layers.TimeDistributed(layers.Dense(self.layer_sizes[1], activation="relu"))(x)
        print(K.int_shape(x))

        x = layers.Flatten()(x)
        print(K.int_shape(x))

        x = layers.Dense(self.layer_sizes[2], activation="relu")(x)
        print(K.int_shape(x))

        x = layers.Dense(self.params)(x)

        encoder_output = layers.BatchNormalization(momentum=BN_M)(x)
        print(K.int_shape(encoder_output))

        self.encoder = Model(encoder_input, encoder_output)

        decoder_input = layers.Input(shape=(self.params,), name='decoder_input')
        print(K.int_shape(decoder_input), "Decoder Input")

        x = layers.Dense(self.layer_sizes[2])(decoder_input)
        if self.training:
            x = layers.BatchNormalization(momentum=BN_M)(x)        
        x = layers.Activation("relu")(x)
        if DO_RATE > 0 and self.training:
            x = layers.Dropout(DO_RATE)(x)
        print(K.int_shape(x))

        x = layers.Dense(TRAIN_BARS * self.layer_sizes[1])(x)
        print(K.int_shape(x))
        x = layers.Reshape((TRAIN_BARS, self.layer_sizes[1]))(x)
        if self.training:
            x = layers.TimeDistributed(layers.BatchNormalization(momentum=BN_M))(x)
        x = layers.Activation("relu")(x)
        if DO_RATE > 0 and self.training:
            x = layers.Dropout(DO_RATE)(x)
        print(K.int_shape(x))

        x = layers.TimeDistributed(layers.Dense(self.layer_sizes[0]))(x)
        if self.training:
            x = layers.TimeDistributed(layers.BatchNormalization(momentum=BN_M))(x)
        x = layers.Activation("relu")(x)
        if DO_RATE > 0 and self.training:
            x = layers.Dropout(DO_RATE)(x)
        print(K.int_shape(x))

        x = layers.TimeDistributed(layers.Dense(SUBDIVISIONS * 4 * MIDI_NOTES, activation="sigmoid"))(x)
        print(K.int_shape(x))

        x = layers.Reshape((TRAIN_BARS, SUBDIVISIONS * 4, MIDI_NOTES))(x)
        print(K.int_shape(x))

        decoder_output = x
        self.decoder = Model(decoder_input, decoder_output)

        model_input = encoder_input
        model_output = self.decoder(encoder_output)
        self.model = Model(model_input, model_output)

    def compile(self, lr):
        self.learning_rate = lr

        optimizer = RMSprop(lr=lr)
        self.model.compile(optimizer=optimizer, loss = "binary_crossentropy")

    def save(self, folder):
        if not os.path.exists(folder):
            os.makedirs(folder)
            os.makedirs(os.path.join(folder, 'viz'))
            os.makedirs(os.path.join(folder, 'weights'))
            os.makedirs(os.path.join(folder, 'images'))

        with open(os.path.join(folder, 'params.pkl'), 'wb') as f:
            pickle.dump([
                self.input_dim
                , self.params
                ], f)

        self.plot_model(folder)

    def load_weights(self, filepath):
        self.model.load_weights(filepath)

    def train_with_generator(self, data_flow, epochs, steps_per_epoch, run_folder, print_every_n_batches = 100, initial_epoch = 0, lr_decay = 1, ):
        custom_callback = CustomCallback(run_folder, print_every_n_batches, initial_epoch, self)
        lr_sched = step_decay_schedule(initial_lr=self.learning_rate, decay_factor=lr_decay, step_size=1)

        checkpoint_filepath=os.path.join(run_folder, "weights/weights-{epoch:03d}-{loss:.2f}.h5")
        checkpoint1 = ModelCheckpoint(checkpoint_filepath, save_weights_only = True, verbose=1)
        checkpoint2 = ModelCheckpoint(os.path.join(run_folder, 'weights/weights.h5'), save_weights_only = True, verbose=1)

        callbacks_list = [checkpoint1, checkpoint2, custom_callback, lr_sched]

        self.model.save_weights(os.path.join(run_folder, 'weights/weights.h5'))
                
        self.model.fit_generator(
            data_flow
            , shuffle = True
            , epochs = epochs
            , initial_epoch = initial_epoch
            , callbacks = callbacks_list
            , steps_per_epoch=steps_per_epoch 
            , workers = 16
            )

    def plot_model(self, run_folder):
        plot_model(self.model, to_file=os.path.join(run_folder ,'viz/model.png'), show_shapes = True, show_layer_names = True)
        plot_model(self.encoder, to_file=os.path.join(run_folder ,'viz/encoder.png'), show_shapes = True, show_layer_names = True)
        plot_model(self.decoder, to_file=os.path.join(run_folder ,'viz/decoder.png'), show_shapes = True, show_layer_names = True)
