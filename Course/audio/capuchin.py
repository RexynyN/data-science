import os
from os.path import join as path
from matplotlib import pyplot as plt
import tensorflow as tf 
import tensorflow_io as tfio

gpus = tf.config.list_physical_devices('GPU')

# if gpus:
#   try:
#     # Currently, memory growth needs to be the same across GPUs
#     for gpu in gpus:
#       tf.config.experimental.set_memory_growth(gpu, True)
#     logical_gpus = tf.config.list_logical_devices('GPU')
#     print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
#   except RuntimeError as e:
#     # Memory growth must be set before GPUs have been initialized
#     print(e)


CAPUCHIN_FILE = os.path.join('data', 'Parsed_Capuchinbird_Clips', 'XC3776-1.wav')
NOT_CAPUCHIN_FILE = os.path.join('data', 'Parsed_Not_Capuchinbird_Clips', 'afternoon-birds-song-in-forest-24.wav')

def load_wav_16k_mono(filename):
    # Load encoded wav file
    file_contents = tf.io.read_file(filename)
    # Decode wav (tensors by channels) 
    wav, sample_rate = tf.audio.decode_wav(file_contents, desired_channels=1)
    # Removes trailing axis (remove last dimensionality of the tensor)
    wav = tf.squeeze(wav, axis=-1)
    sample_rate = tf.cast(sample_rate, dtype=tf.int64)
    # Goes from 44100Hz to 16000hz - amplitude of the audio signal
    wav = tfio.audio.resample(wav, rate_in=sample_rate, rate_out=16000)
    return wav

wave = load_wav_16k_mono(CAPUCHIN_FILE)
nwave = load_wav_16k_mono(NOT_CAPUCHIN_FILE)

plt.plot(wave)
plt.plot(nwave)
plt.show()

POS = path('data', 'Parsed_Capuchinbird_Clips')
NEG = path('data', 'Parsed_Not_Capuchinbird_Clips')

# %% [markdown]
# ## 3.2 Create Tensorflow Datasets

# %%
# Create a TensorFlow datasets
# when on linux, change to "/*.wav"
pos = tf.data.Dataset.list_files(POS+'/*.wav')
neg = tf.data.Dataset.list_files(NEG+'/*.wav')

# %% [markdown]
# ## 3.3 Add labels and Combine Positive and Negative Samples

# %%
# Positives will be 1's
positives = tf.data.Dataset.zip((pos, tf.data.Dataset.from_tensor_slices(tf.ones(len(pos)))))
# Negatives will be 0's
negatives = tf.data.Dataset.zip((neg, tf.data.Dataset.from_tensor_slices(tf.zeros(len(neg)))))
# Concatenate both samples
data = positives.concatenate(negatives)

print(positives.as_numpy_iterator().next())
data.shuffle(1000).as_numpy_iterator().next()

# %% [markdown]
# # 4. Determine Average Length of a Capuchin Call

# %% [markdown]
# ## 4.1 Calculate Wave Cycle Length

# %%
lengths = []
for file in os.listdir(os.path.join('data', 'Parsed_Capuchinbird_Clips')):
    tensor_wave = load_wav_16k_mono(os.path.join('data', 'Parsed_Capuchinbird_Clips', file))
    lengths.append(len(tensor_wave))

# %% [markdown]
# ## 4.2 Calculate Mean, Min and Max

# %%
tf.math.reduce_mean(lengths)
print("Média: ", tf.math.reduce_mean(lengths).numpy()/16000)
print("Mínimo: ", tf.math.reduce_min(lengths).numpy()/16000)
print("Máximo: ", tf.math.reduce_max(lengths).numpy()/16000)

# %% [markdown]
# # 5. Build Preprocessing Function to Convert to Spectrogram

# %% [markdown]
# ## 5.1 Build Preprocessing Function

# %%
# Function that creates a 
def preprocess(file_path, label): 
    wav = load_wav_16k_mono(file_path)
    wav = wav[:48000]
    # Not all audios have 48000 so pad the start of the audio with zeros
    zero_padding = tf.zeros([48000] - tf.shape(wav), dtype=tf.float32)
    wav = tf.concat([zero_padding, wav],0)
    # stft = Short Time Fourier Transform
    spectrogram = tf.signal.stft(wav, frame_length=320, frame_step=32)
    spectrogram = tf.abs(spectrogram)
    spectrogram = tf.expand_dims(spectrogram, axis=2)
    return spectrogram, label

# %% [markdown]
# ## 5.2 Test Out the Function and Viz the Spectrogram

# %%
filepath, label = positives.shuffle(buffer_size=10000).as_numpy_iterator().next()

# %%
spectrogram, label = preprocess(filepath, label)

# %%
plt.figure(figsize=(30,20))
plt.imshow(tf.transpose(spectrogram)[0])
plt.show()

# %% [markdown]
# # 6. Create Training and Testing Partitions

# %% [markdown]
# ## 6.1 Create a Tensorflow Data Pipeline

# %%
# Create the TensorFlow data pipeline
data = data.map(preprocess) # Create the spectrogram for all audios
data = data.cache() # Cache it
data = data.shuffle(buffer_size=1000) # Randomize it
data = data.batch(16) # Create batches for training, 16 spectrograms at a time
data = data.prefetch(8) # Pre fetch 8 for performance

# %% [markdown]
# ## 6.2 Split into Training and Testing Partitions

# %%
from math import ceil

# Partition the train and test data 
TRAIN = ceil(len(data) * 0.7)

train = data.take(TRAIN)
test = data.skip(TRAIN).take(len(data) - TRAIN)

# %% [markdown]
# ## 6.3 Test One Batch

# %%
samples, labels = train.as_numpy_iterator().next()

# %%
samples.shape

# %% [markdown]
# # 7. Build Deep Learning Model

# %% [markdown]
# ## 7.1 Load Tensorflow Dependencies

# %%
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, Dense, Flatten

# %% [markdown]
# ## 7.2 Build Sequential Model, Compile and View Summary

# %%
# Build the model
model = Sequential()

model.add(Conv2D(16, (3,3), activation='relu', input_shape=(1491, 257,1)))
model.add(Conv2D(16, (3,3), activation='relu'))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dense(1, activation='sigmoid'))

# %%

# Compile it
model.compile('Adam', loss='BinaryCrossentropy', metrics=[tf.keras.metrics.Recall(),tf.keras.metrics.Precision()])

# %%
# See the summary of it
model.summary()

# %% [markdown]
# ## 7.3 Fit Model, View Loss and KPI Plots

# %%
# Train it :^)
hist = model.fit(train, epochs=4, validation_data=test)

# %%
plt.title('Loss')
plt.plot(hist.history['loss'], 'r')
plt.plot(hist.history['val_loss'], 'b')
plt.show()

# %%
plt.title('Precision')
plt.plot(hist.history['precision'], 'r')
plt.plot(hist.history['val_precision'], 'b')
plt.show()

# %%
plt.title('Recall')
plt.plot(hist.history['recall'], 'r')
plt.plot(hist.history['val_recall'], 'b')
plt.show()

# %% [markdown]
# # 8. Make a Prediction on a Single Clip

# %% [markdown]
# ## 8.1 Get One Batch and Make a Prediction

# %%
X_test, y_test = test.as_numpy_iterator().next()

# %%
yhat = model.predict(X_test)

# %% [markdown]
# ## 8.2 Convert Logits to Classes 

# %%
yhat = [1 if prediction > 0.5 else 0 for prediction in yhat]
yhat

# %% [markdown]
# # 9. Build Forest Parsing Functions

# %% [markdown]
# ## 9.1 Load up MP3s

# %%
def load_mp3_16k_mono(filename):
    """ Load a WAV file, convert it to a float tensor, resample to 16 kHz single-channel audio. """
    res = tfio.audio.AudioIOTensor(filename)
    # Convert to tensor and combine channels 
    tensor = res.to_tensor()
    tensor = tf.math.reduce_sum(tensor, axis=1) / 2 
    # Extract sample rate and cast
    sample_rate = res.rate
    sample_rate = tf.cast(sample_rate, dtype=tf.int64)
    # Resample to 16 kHz
    wav = tfio.audio.resample(tensor, rate_in=sample_rate, rate_out=16000)
    return wav

# %%
mp3 = os.path.join('data', 'Forest Recordings', 'recording_00.mp3')

# %%
wav = load_mp3_16k_mono(mp3)

# %%
audio_slices = tf.keras.utils.timeseries_dataset_from_array(wav, wav, sequence_length=48000, sequence_stride=48000, batch_size=1)
# Number of sections of the audio to feed to the model
len(audio_slices)

# %%
samples, index = audio_slices.as_numpy_iterator().next()
# Shape of one section
samples.shape 

# %% [markdown]
# ## 9.2 Build Function to Convert Clips into Windowed Spectrograms

# %%
# Create a spectrogram from an MP3
def preprocess_mp3(sample, index):
    sample = sample[0]
    zero_padding = tf.zeros([48000] - tf.shape(sample), dtype=tf.float32)
    wav = tf.concat([zero_padding, sample],0)
    spectrogram = tf.signal.stft(wav, frame_length=320, frame_step=32)
    spectrogram = tf.abs(spectrogram)
    spectrogram = tf.expand_dims(spectrogram, axis=2) 
    return spectrogram

# %% [markdown]
# ## 9.3 Convert Longer Clips into Windows and Make Predictions

# %%
audio_slices = tf.keras.utils.timeseries_dataset_from_array(wav, wav, sequence_length=48000, sequence_stride=48000, batch_size=1)
audio_slices = audio_slices.map(preprocess_mp3)
audio_slices = audio_slices.batch(64)

# %%
yhat = model.predict(audio_slices)
yhat = [1 if prediction > 0.99 else 0 for prediction in yhat]
yhat

# %% [markdown]
# ## 9.4 Group Consecutive Detections

# %%
from itertools import groupby

# %%
yhat = [key for key, group in groupby(yhat)]
calls = tf.math.reduce_sum(yhat).numpy()

# %%
calls

# %% [markdown]
# # 10. Make Predictions

# %% [markdown]
# ## 10.1 Loop over all recordings and make predictions

# %%
results = {}
for file in os.listdir(os.path.join('data', 'Forest Recordings')):
    FILEPATH = os.path.join('data','Forest Recordings', file)
    
    wav = load_mp3_16k_mono(FILEPATH)
    audio_slices = tf.keras.utils.timeseries_dataset_from_array(wav, wav, sequence_length=48000, sequence_stride=48000, batch_size=1)
    audio_slices = audio_slices.map(preprocess_mp3)
    audio_slices = audio_slices.batch(64)
    
    yhat = model.predict(audio_slices)
    
    results[file] = yhat

# %%
results

# %% [markdown]
# ## 10.2 Convert Predictions into Classes

# %%
class_preds = {}
for file, logits in results.items():
    class_preds[file] = [1 if prediction > 0.99 else 0 for prediction in logits]
class_preds

# %% [markdown]
# ## 10.3 Group Consecutive Detections

# %%
postprocessed = {}
for file, scores in class_preds.items():
    postprocessed[file] = tf.math.reduce_sum([key for key, group in groupby(scores)]).numpy()
postprocessed

# %% [markdown]
# # 11. Export Results

# %%
import csv

# %%
with open('capuchinbird_results.csv', 'w', newline='') as f:
    writer = csv.writer(f, delimiter=',')
    writer.writerow(['recording', 'capuchin_calls'])
    for key, value in postprocessed.items():
        writer.writerow([key, value])


model.save('my_model.h5')