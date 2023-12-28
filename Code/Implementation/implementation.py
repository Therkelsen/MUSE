# Tensorflow / Keras
import tensorflow as tf
from tensorflow import keras
print('Tensorflow version:', tf.__version__)
from keras.models import Sequential # for creating a linear stack of layers for our Neural Network
from keras.layers import Input # for instantiating a keras tensor
from keras.layers import GRU, Dense, GRU, Dropout, concatenate, Activation, Concatenate, Flatten, BatchNormalization# for creating layers inside the Neural Network
from keras.models import load_model, Model
from keras.optimizers import Adam
from keras.initializers import he_normal
from keras.regularizers import l2

class Ada_con():

    def load_nn_model(self, model_path):
        # Assuming loaded_model_path is the path to your saved model file
        loaded_model = load_model(model_path)
        print("Model loaded successfully.")
        print(loaded_model.summary())
        return loaded_model




if __name__ == '__main__':
    ac = Ada_con()
    loaded_model_path = 'Code/Implementation/second_L2_Batch_16feat_30ts_50ep.keras'
    loaded_model = keras.models.load_model(loaded_model_path)
    print("Model loaded successfully.")
    print(loaded_model.summary())
    # loaded_model = ac.load_nn_model(loaded_model_path)
