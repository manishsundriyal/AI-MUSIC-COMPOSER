import os
import numpy as np
from keras.models import Sequential
from keras.layers.recurrent import LSTM
from keras.layers.core import Dense, Dropout

from midi_functions_lib.midi_sequence import midi_to_sequence, sequence_to_midi
from midi_functions_lib.midi_compress import compress_state_matrix, decompress_state_matrix

import datetime

def load_data_from_midi_files():

	state_matrix = []
	for subdir, dirs, files in os.walk('MIDI_MUSIC'):
		for file in files:
			print 'Reading "' + file + '"...\n'
			file_path = os.path.join(subdir,file)
			state_matrix.extend(midi_to_sequence(file_path)[0])
	return state_matrix


def preprocess_data(state_matrix,timestep_size):

	
	X = []
	Y = []

	step_size = 1

	for i in xrange(0, len(state_matrix) - timestep_size, step_size):
		data_point_x = state_matrix[i: i + timestep_size]
		X.append(data_point_x)
		data_point_y = state_matrix[i + timestep_size]
		Y.append(data_point_y)

	return X, Y



def main():

	print 'Reading all the MIDI Files...\n'
	state_matrix = load_data_from_midi_files();
	print 'Reading all the MIDI Files Completed\n'

	print 'Compressing Files..\n'
	compression_ratio = 10
	print 'Compression Ratio =',compression_ratio

	state_matrix, post_compression_columns = compress_state_matrix(state_matrix,compression_ratio)
	print 'Compression Completed\n'

	timestep_size = 50
	print 'Converting state_matrix into 3D Array of dimensions: Samples x Timesteps x Features\n'
	X, Y = preprocess_data(state_matrix,timestep_size)
	print 'Conversion Completed\n'

	print 'Casting to numpy-array...\n'
	X, Y = np.array(X), np.array(Y)
	print 'Casting Completed\n'

	print 'Dimensions of X:',X.shape,'\n'
	print 'Dimensions of Y:',Y.shape,'\n'

	print 'Building Model...\n'

	min_nodes = 128
	nb_nodes = max(X.shape[2],min_nodes)

	model = Sequential()
	print 'Adding 1st Layer...\n'
	model.add(LSTM(nb_nodes,input_shape=(X.shape[1],X.shape[2]),return_sequences=True))
	model.add(Dropout(0.2))
	print 'Adding 2nd Layer...\n'
	model.add(LSTM(2*nb_nodes))
	model.add(Dropout(0.2))
	print 'Adding 3rd Layer...\n'
	model.add(Dense(X.shape[2]))
	model.add(Dropout(0.2))

	print 'Building Model Completed\n'


	print 'Compiling Model...\n'
	model.compile(loss='mean_squared_error',
	                  optimizer="rmsprop", metrics=['accuracy'])
	print 'Compiling Model Finished!\n'

	print 'Training Model..\n'
	model.fit(X,Y,validation_split=0.2)
	print 'Training Model Completed\n'


	print 'Predicting...\n'
	predictions = model.predict(X, batch_size=32, verbose=1)
	print 'Predicting Finished\n'

	print 'Predictions Dimensions:',predictions.shape,'\n'


	predictions = predictions.astype(int).clip(min=0)

	predictions = predictions.tolist()

	print 'Decompressing Files...\n'
	predictions = decompress_state_matrix(predictions,post_compression_columns)
	print 'Decompressing Finished\n'

	print 'Writing to output file ...\n'
	out_file_path = 'output/' + \
	    str(datetime.datetime.now()).replace(
	        ' ', '_').replace(':', '_') + '.mid'
	sequence_to_midi(predictions, out_file_path, (100, None))
	print 'Writing to output file done!\n'


if __name__ == '__main__':
    main()