# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#!/usr/bin/env python

from midiutil import MIDIFile
import os
import numpy as np

os.chdir('C:/Users/woody/OneDrive/Documents/githubrepos/generative_music/first_tests')

# Define initial parameters
track = 0
time = 0    # In beats
time_section = 0
tempo = 60   # In BPM
volume  = 100  # 0-127, as per the MIDI standard
channel  = 0
root = 45
root_values = np.array([root, root-2, root+5, root+7])
root_weights = np.array([0.5, 0.1, 0.1, 0.3])
root_sequence = np.array([root])
n_sections = 10

# generate random sequence of root notes based on the above
root_rand = np.random.choice(root_values,size=n_sections, p=root_weights)
root_sequence = np.concatenate((root_sequence,root_rand), axis = None)
print(root_sequence)

# define transition weights over upper and lower interval
# you can pick any values you want.  This is just an intuitive way for you
# to define the relative probabilites of each interval.  the ith entery in
# weights corresponds to the i+1th and -(i+1)th interval.  root_weight 
# is the probability of sampling the root note again.
weights = [0,0,0,1,10,0,10,0,0,0,0,0]
root_weight = [15]
rev_weights = weights[::-1]
all_weights = rev_weights + root_weight + weights

weights_array = np.array(all_weights)
probs_array = weights_array / np.sum(weights_array) # normalize weights
# probs array is a probability distribution over the two-octave interval
# around the current note

# Create midifile objects for two instruments
MyMIDI_1 = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
                      # automatically
MyMIDI_2 = MIDIFile(1)
MyMIDI_1.addTempo(track, time, tempo)
MyMIDI_2.addTempo(track, time, tempo)

for root in root_sequence: 
    
    degrees  = range(-12,13)  # MIDI note number
    lower_bound = root - 12
    upper_bound = root + 12
    duration = 10   # In beats

    amount_of_notes = int(round(np.random.normal(loc=5,scale=1),0))
    pitch_delta = 0
    
    MyMIDI_1.addNote(track, channel, root, time, duration, volume)
    #MyMIDI_1.addNote(track, channel, root+12, time, duration, volume)
    
    for i in range(0, amount_of_notes):
        
        # time of current note is normal distribution centered around
        # 2 seconds before previous note ends, with max at end of previous note
        time = min(np.random.normal(loc=time + duration - 2,scale = 1), 
                   time + duration)
        
        # duration is sampled from normal distribution with mean 4 and sd 2
        duration = np.random.normal(loc=10,scale=0.5)
        
        # the next pitch is sampled as an interval relative to the root pitch
        
        # create a copy of the weights array and assign the previous interval
        # to 0 probability so that the same pitch is never played two times
        # in a row
        temp_weights_array = np.copy(weights_array)
        temp_weights_array[pitch_delta+12] = 0
        probs_array = temp_weights_array / np.sum(temp_weights_array)
        pitch_delta = np.random.choice(degrees, p = probs_array)
        pitch = root + pitch_delta
        
        # re-adjust pitchc if it goes out of two octive range
        if pitch > upper_bound:
            pitch = pitch - 12
        if pitch < lower_bound:
            pitch = pitch + 12
        
        # pitch and octave are both written
        MyMIDI_1.addNote(track, channel, pitch, time, duration, volume)
        #MyMIDI_1.addNote(track, channel, pitch+12, time, duration, volume)

    ### Write Drone To Instrument 2
    length_of_section = time + duration - time_section
    drone_start = time_section
    print(time_section, length_of_section)
    MyMIDI_2.addNote(track, channel, root+10, drone_start, length_of_section, volume)
    time_section = time_section + length_of_section
    
# Write to File
with open("two_pitch_instrument_1.mid", "wb") as output_file:
    MyMIDI_1.writeFile(output_file)
    
with open("two_pitch_instrument_2.mid", "wb") as output_file:
    MyMIDI_2.writeFile(output_file)
    
