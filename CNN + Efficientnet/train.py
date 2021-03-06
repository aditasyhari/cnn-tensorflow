# -*- coding: utf-8 -*-
"""train.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Hj1FuiXvJJTsLlbelML06rCoPV_OtHWj
"""

from google.colab import drive
drive.mount('/content/drive')

import tensorflow as tf
import os
from tensorflow.keras.preprocessing.image import ImageDataGenerator

dim = (150, 150)
channel = (3, )
input_shape = dim + channel
batch_size = 16
epoch = 20

train_datagen = ImageDataGenerator(rescale = 1. / 255,
                                    shear_range = 0.2,
                                    zoom_range = 0.2,
                                    horizontal_flip = True)

test_datagen = ImageDataGenerator(rescale = 1. / 255,
                                    shear_range = 0.2,
                                    zoom_range = 0.2,
                                    horizontal_flip = True)

val_datagen = ImageDataGenerator(rescale = 1. / 255,
                                    shear_range = 0.2,
                                    zoom_range = 0.2,
                                    horizontal_flip = True)

train_generator = train_datagen.flow_from_directory('/content/drive/MyDrive/Colab Notebooks/Data Pitaya(Validasi)/train',
                                                    target_size = dim,
                                                    batch_size = batch_size,
                                                    class_mode = 'categorical',
                                                    shuffle = True)

test_generator = test_datagen.flow_from_directory('/content/drive/MyDrive/Colab Notebooks/Data Pitaya(Validasi)/test',
                                                    target_size = dim,
                                                    batch_size = batch_size,
                                                    class_mode = 'categorical',
                                                    shuffle = True)

val_generator = val_datagen.flow_from_directory('/content/drive/MyDrive/Colab Notebooks/Data Pitaya(Validasi)/validation',
                                                    target_size = dim,
                                                    batch_size = batch_size,
                                                    class_mode = 'categorical',
                                                    shuffle = True)

num_class = test_generator.num_classes
labels = train_generator.class_indices.keys()

print(labels)

def tf_data_generator(generator, input_shape):
    num_class = generator.num_classes
    tf_generator = tf.data.Dataset.from_generator(
        lambda: generator,
        output_types = (tf.float32, tf.float32),
        output_shapes = ([None,
                         input_shape[0],
                         input_shape[1],
                         input_shape[2]],
                        [None, num_class])
    )
    return tf_generator

train_data = tf_data_generator(train_generator, input_shape)
test_data = tf_data_generator(test_generator, input_shape)
val_data = tf_data_generator(val_generator, input_shape)

pip install -U --pre efficientnet

from efficientnet.tfkeras import EfficientNetB1
from tensorflow.keras import layers, Sequential
from tensorflow.keras.models import Model

# base models
base_model = EfficientNetB1(
    input_shape = input_shape,
    include_top = False,
    weights = 'noisy-student',
    classes = num_class,
)

# custom layers
x = base_model.output
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.5)(x)
x = layers.Dense(1024, activation = 'relu')(x)

predictions = layers.Dense(num_class, activation = 'softmax')(x)
model = Model(inputs = base_model.input, outputs = predictions)

model.summary()

# Compile the model
print('Compiling Model...')
model.compile(optimizer = 'adam',
             loss = 'categorical_crossentropy',
             metrics = ['accuracy'])

# Train Model
history = model.fit(x=train_data,
                   steps_per_epoch = len(train_generator),
                   epochs = epoch,
                   validation_data = val_data,
                   validation_steps = len(val_generator),
                   shuffle = True,
                   verbose = 1)

# Save Model
MODEL_BASE_PATH = "/content/drive/My Drive/Colab Notebooks/model"
PROJECT_NAME = "pitaya"
SAVE_MODEL_NAME = "model20_efficientnet.h5"
save_model_path = os.path.join(MODEL_BASE_PATH, PROJECT_NAME, SAVE_MODEL_NAME)

if os.path.exists(os.path.join(MODEL_BASE_PATH, PROJECT_NAME)) == False:
    os.makedirs(os.path.join(MODEL_BASE_PATH, PROJECT_NAME))
    
print('Saving Model At {}...'.format(save_model_path))
model.save(save_model_path,include_optimizer=True)

# Evaluasi Model
# loss, acc = model.evaluate(test_data, steps = len(test_generator), verbose = 0)
# print('Accuracy pada data training: {:.4f} \nLoss pada data training: {:.4f}'.format(acc, loss), '\n')

# loss, acc = model.evaluate(test_data, steps = len(test_generator), verbose = 0)
# print('Accuracy pada data test: {:.4f} \nLoss pada data test: {:.4f}'.format(acc, loss), '\n')