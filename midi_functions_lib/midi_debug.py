
import midi
from pprint import pprint


def desparsify_state(state):
    
    ret = []
    for pitch, volume in enumerate(state):
        if volume > 0:
            ret.append(pitch)
    return ret


def desparsify_state_matrix(state_matrix):
    
    ret = ""
    for idx, state in enumerate(state_matrix):
        ret += str(idx) + ".) " + str(desparsify_state(state)) + "\n"
    return ret


def main():
    file_path = 'out.mid'
    pattern = midi.read_midifile(file_path)
    print pattern


if __name__ == '__main__':
    main()
