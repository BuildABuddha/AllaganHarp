# AllaganHarp
A prototype tool used to "arpeggiate" chords in MIDI files so they can be played in FFXIV using Bard Music Player with instruments like harps or lutes.

In Final Fantasy XIV, bards can really only play one note at a time, which severely limits their ability to play chords... but doesn't entirely remove it. To play a chord, notes have to be "rolled", or played one at a time very quickly. Luckily, this sounds good in-game on harps and lutes, like you're strumming on the strings. This does mean that any MIDI files you use with programs like Bard Music Player have to be tediously edited so that all chords are slightly arpeggiated, though. 

This program automates this process! Give it a MIDI file you want to edit, and an arpeggio spacing time (0.035 seconds is a good start, btw), and it will spit out a midi that is suitable for playing on a harp in FFXIV using Bard Music Player! 

There are still a number of edge cases to accomidate for and issues to fix, so it can't fix EVERYTHING about every MIDI file. However, this will likely save you a bit of work when you're making songs. 

## Installation
1) Download AllaganHarp.exe from the [releases page.](https://github.com/BuildABuddha/AllaganHarp/releases)

2) Move AllaganHarp.exe to the same directory as FFBardMusicPlayer.exe. This is so that it has access to the "songs" directory where you hopefully store all your MIDI files.

3) That's it! 

## Usage
1) Double click on AllaganHarp.exe.

2) The program will ask for the name of the file you want to arpeggiate. I would reccomend copy/pasting it in. 

3) It will then ask you what the new .mid file will be named. By default, it will simply add " (Harp).mid" to the end of the filename. 

4) Select how long you want your arpeggio spacing to be. It will reccomend 0.035, which has worked best for me in my personal testing. If you are not running consistantly at 60 FPS, you may need to raise this number. 

5) If all things worked as planned, it should get to work creating your new MIDI file and save it in your "songs" directory! 

## Best Practices
Right now, the program looks for chords by looking for "note_on" messages that start exactly on the same tick. Usually this is enough, but sometimes notes start 1 tick after another note in the chord, and this can mess things up. There are plans in the future to have it look for chords where some of the notes might be a tick or two off. If a chord doesn't get arpeggiated right, go back to the original file and make sure all the notes start on the same tick.

The program won't adjust your octaves. You'll have to do that yourself. The default range for Bard Music Player is C3 to C6, so I would reccomend fixing your song so it's within those three octaves before you feed it to AllaganHarp. 

Lastly, AllaganHarp reduces all notes to length 0 for simplicity. This might change in the future, but for now, the best way to deal with this is to simply switch your midi's instrument to the Orchestral Harp, an instrument that has reverb independant of the length of the note. It also sounds very close to what the in-game harp sounds like, so you get a nice idea of what it'll sound like! 
