from mido import Message, MidiFile, MidiTrack
import mido
import math
import os
import sys


class SongData:
    def __init__(self, filename, spacing, verbose=True):
        self.spacing = spacing
        self.filename = filename
        self.verbose = verbose

        self.original_midi = MidiFile(os.path.join(os.path.dirname(__file__), "songs", filename))
        self.new_midi = MidiFile()
        self.new_track = MidiTrack()
        self.new_midi.tracks.append(self.new_track)
        self.new_midi.ticks_per_beat = self.original_midi.ticks_per_beat
        self.event_dict = {}
        self.create_event_dict()

    def create_event_dict(self):
        self.event_dict = {}
        for track in self.original_midi.tracks:
            # We need to convert "delta time" into "absolute time" and use this to collect events.
            absolute_time = 0
            for message in track:
                # If any time has passed since the last message, add it to absolute_time.
                absolute_time = absolute_time + message.time

                # Add timestamp to our dictionary in absolute time (time since start of file)
                if absolute_time not in self.event_dict:
                    self.event_dict[absolute_time] = {
                        "note_on": [],
                        "note_off": [],  # This might be useful later? For now we reduce all notes to length 0.
                        "non_note": []
                    }

                # Collect events in our dictionary
                if message.is_meta or message.type not in ['note_on', 'note_off']:
                    self.event_dict[absolute_time]["non_note"].append(message)
                elif message.type is 'note_on':
                    self.event_dict[absolute_time]["note_on"].append(message)
                else:
                    pass
                    # event_dict[absolute_time]["note_off"].append(message)
        # End of for track in tracks loop

        self.remove_note_off_events()
        self.remove_duplicate_notes()

    def remove_note_off_events(self):
        # Get rid of timestamps where the only thing that's happening is a note turning off.
        for key in self.event_dict.copy().keys():
            if not (self.event_dict[key]["note_on"] or self.event_dict[key]["non_note"]):
                del self.event_dict[key]

    def remove_duplicate_notes(self):
        # Get rid of duplicate notes:
        for key in self.event_dict.copy().keys():
            temp_list = []
            new_notes = []
            for event in self.event_dict[key]["note_on"]:
                if event.note not in temp_list:
                    temp_list.append(event.note)
                    new_notes.append(event)
                else:
                    if self.verbose:
                        print("Duplicate note found at time:", key)
            self.event_dict[key]["note_on"] = new_notes

    @staticmethod
    def get_note_number(note_message):
        return note_message.note

    def verbose_print(self, *args):
        if self.verbose:
            print(*args)
        else:
            pass

    def build_track(self):
        last_message_time = 0
        time_to_subtract = 0
        current_tempo = 500000
        self.new_track = MidiTrack()

        for key in sorted(self.event_dict.keys()):
            self.verbose_print("\nTime:", key)
            # if self.verbose:
            #     print("\nTime:", key)

            arpeggio_spacing = math.ceil(mido.second2tick(self.spacing, self.new_midi.ticks_per_beat, current_tempo))
            current_spacing = 0

            for message in self.event_dict[key]["non_note"]:
                # Convert from the timestamp's absolute time to delta time:
                delta_time = key - last_message_time - time_to_subtract
                if (time_to_subtract > 0) and (delta_time < arpeggio_spacing):
                    print("WARNING, ARPEGGIO SPACING CREATES TOO BIG A DELAY AT TIME =", key)
                    delta_time = arpeggio_spacing
                time_to_subtract = 0

                new_message = message.copy()
                new_message.time = delta_time
                self.verbose_print(new_message)
                self.new_track.append(new_message)
                last_message_time = key

                if message.type == 'set_tempo':
                    current_tempo = message.tempo
                    arpeggio_spacing = math.ceil(
                        mido.second2tick(self.spacing, self.new_midi.ticks_per_beat, current_tempo))

            # note_off events were deleted and replaced to make all notes length 0. Nothing happens here.
            for message in self.event_dict[key]["note_off"]:
                pass

            # Sort keys in ascending order.
            for message in sorted(self.event_dict[key]["note_on"], key=lambda x: self.get_note_number(x)):
                # Convert from the timestamp's absolute time to delta time:
                delta_time = key - last_message_time - time_to_subtract
                if (time_to_subtract > 0) and (delta_time < arpeggio_spacing):
                    print("WARNING, ARPEGGIO SPACING CREATES TOO BIG A DELAY AT TIME =", key)
                    delta_time = arpeggio_spacing
                time_to_subtract = 0

                new_message = message.copy()
                new_message.time = delta_time + current_spacing
                current_spacing = arpeggio_spacing
                self.verbose_print(new_message)
                self.new_track.append(new_message)
                self.new_track.append(Message('note_off',
                                              channel=new_message.channel,
                                              note=new_message.note,
                                              velocity=new_message.velocity,
                                              time=0))
                last_message_time = key

            if len(self.event_dict[key]["note_on"]) > 1:
                time_to_subtract = (len(self.event_dict[key]["note_on"]) - 1) * arpeggio_spacing
            else:
                time_to_subtract = 0

        self.new_midi.tracks[0] = self.new_track

    def save(self, new_midi_filename):
        self.new_midi.save(os.path.join(os.path.dirname(__file__), "songs", new_midi_filename))


# if __name__ == '__main__':
if True:
    print("<BEEP> Allagan Music Processing Node activated. This module is for processing music in .mid format for",
          "easier solo play on instruments like harp or lute. Please follow these instructions to the best of your",
          "ability for best results.")

    SONGS_DIRECTORY = os.path.join(os.path.dirname(__file__), "songs")
    if not os.path.exists(SONGS_DIRECTORY):
        print("WARNING: There does not appear to be a 'songs' directory. I will create one for you. Please take this",
              "opportunity to copy any songs you wish me to process into this directory. \nPress enter to exit.")
        os.mkdir(SONGS_DIRECTORY)
        
        text=input()
        sys.exit(text)

    midCounter = 0
    for _, _, files in os.walk(SONGS_DIRECTORY):
        for file in files:
            if file.endswith('.mid'):
                midCounter += 1
    if midCounter == 0:
        print("\n\nThere appears to be no .mid files in the songs directory. Please copy any songs you wish me to process",
              "into this directory and try again. \nPress enter to exit.")
        
        text=input()
        sys.exit(text)

    # Get the song filename and check if it exists.
    song_filename = ""
    while not song_filename:
        song_filename = input("What file in your 'songs' directory would you like me to process? \n").strip()
        if not os.path.exists(os.path.join(SONGS_DIRECTORY, song_filename)) \
                and not os.path.exists(os.path.join(SONGS_DIRECTORY, song_filename + '.mid')):
            print("\n\nIt appears that file does not exist. Try copy/pasting its name into this interface.")
            song_filename = ""
    if not song_filename[-4:] == ".mid":  # User doesn't have to add '.mid', we'll do that for them!
        song_filename = song_filename + ".mid"

    # Confirm new filename.
    new_filename = song_filename.replace(".mid", "") + " (Harp).mid"
    response = input("The new file will be called " + new_filename + "\nIs this okay? (y/n)\n").strip().lower()[0]
    if not response == 'y':
        new_filename = input("Please input the new file's name:\n").strip()
        if not new_filename[-4:] == ".mid":
            new_filename = new_filename + ".mid"
        print("The new file's name will be", new_filename)

    arpeggio_spacing = None
    while not arpeggio_spacing:
        try:
            print("How many seconds would you like to make your arpeggio spacing? This is the time between each note",
                  "in a chord. \nFor those who can reliably play at 60 FPS, the recommended time is 0.035 seconds.")
            arpeggio_spacing = float(input())
        except ValueError:
            print("Hmm, that doesn't appear to be a number. Try again.")
            arpeggio_spacing = None

    print("I will now attempt to create your song...")
    new_song = SongData(song_filename, arpeggio_spacing)
    new_song.build_track()
    new_song.save(new_filename)

    print("The song has been saved.")

    print("Goodbye!")
    input()
