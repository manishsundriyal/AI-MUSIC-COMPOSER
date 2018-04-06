
import midi
from copy import copy
from pprint import pprint


def midi_to_sequence(filepath):
   
    state_matrix = []

    pattern = midi.read_midifile(filepath)


    tempo_event = None

    for track in pattern:
    
        state = [0] * 128
        for event in track:
            if isinstance(event, midi.EndOfTrackEvent):
                state_matrix += [copy(state)]
                break
            elif isinstance(event, midi.NoteEvent):
                if event.tick > 0:
                   
                    state_matrix += event.tick * [copy(state)]
                if isinstance(event, midi.NoteOffEvent):

                    state[event.pitch] = 0
                else:
                    state[event.pitch] = event.data[1]


        for i in xrange(min(10, len(track))):
            if isinstance(track[i], midi.SetTempoEvent):
                tempo_event = track[i]
                break

    return state_matrix, (pattern.resolution, tempo_event)


def get_next_different_state(state_matrix, index):
    
    for i in xrange(index + 1, len(state_matrix)):
        if state_matrix[i] != state_matrix[index]:
            return i
    return len(state_matrix)


def state_diff(current_state, next_state):
    
    notes_on = []
    notes_off = []

    for pitch, (volume1, volume2) in enumerate(zip(current_state, next_state)):
        if volume1 == 0 and volume2 > 0:
            notes_on.append([pitch, volume2])
        elif volume1 > 0 and volume2 == 0:
            notes_off.append([pitch, volume2])

    return (notes_on, notes_off)


def sequence_to_midi(state_matrix, filepath, meta_info=None):
    
    resolution, tempo_event = meta_info if meta_info else None

    pattern = midi.Pattern(resolution=resolution)
    track = midi.Track()
    pattern.append(track)
    if tempo_event:
        track.append(tempo_event)

    notes_on, _ = state_diff([0] * 128, state_matrix[0])
    for note in notes_on:
        track.append(midi.NoteOnEvent(tick=0, channel=0, data=note))

    current_state_index = 0
    while current_state_index < len(state_matrix):
        next_state_index = get_next_different_state(
            state_matrix, current_state_index)
        ticks_elapsed = next_state_index - current_state_index

        current_state = state_matrix[current_state_index]
        next_state = state_matrix[next_state_index] if next_state_index < len(
            state_matrix) else [0] * 128
        notes_on, notes_off = state_diff(current_state, next_state)

        for note in notes_on:
            track.append(midi.NoteOnEvent(
                tick=ticks_elapsed, channel=0, data=note))

            ticks_elapsed = 0

        for note in notes_off:
            track.append(midi.NoteOffEvent(
                tick=ticks_elapsed, channel=0, data=note))
            ticks_elapsed = 0

        current_state_index = next_state_index

    track.append(midi.EndOfTrackEvent(tick=1))
    midi.write_midifile(filepath, pattern)

    return pattern


def main():
    filepath = 'debug.mid'
    state_matrix, meta_info = midi_to_sequence(filepath)
    pattern = sequence_to_midi(state_matrix, 'out.mid', meta_info)


if __name__ == '__main__':
    main()
