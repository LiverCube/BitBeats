# Copyright (C) 2024 Hannes PESCOLLER, Eugen-Maximilian STANGL

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see https://www.gnu.org/licenses/

import cmd
import OSC
import time

class BitBeats(cmd.Cmd):
    def __init__(self, filename=None):
        super().__init__()
        self.prompt = "BitBeats> "
        self.channels = {"triangle": "/triangle", "square1": "/square1", "square2": "/square2", "noise": "/noise"}
        self.current_channel = None
        self.filename = filename
        self.oscillators = []
        self.variables = {}
        self.tempo=60

    def do_run_script(self, script_file):
        """Runs commands from a script file"""
        try:
            with open(script_file) as f:
                for line in f.readlines():
                    clean_line = line.strip()
                    # Check if the line is a comment or empty
                    if clean_line.startswith("#"):
                        continue  # Skip comments and empty lines
                    # Check if the line defines a variable
                    if '=' in clean_line:
                        self.onecmd_define_variable(clean_line)
                    else:
                        # Replace variables in the line with their values
                        for variable_name, value in self.variables.items():
                            clean_line = clean_line.replace(variable_name, value)
                        self.onecmd(clean_line)
        except FileNotFoundError:
            print(f"ERROR: Script file '{script_file}' not found")
            self.do_stop()
        except ValueError as e:
            print(f"ERROR: {e}: Stopping the script.")
            self.do_stop()
        except KeyboardInterrupt:
            print("KeyboardInterrupt: Stopping the script.")
            self.do_stop()
        except Exception as e:
            print(f"ERROR: {e}: Stopping the script.")
            self.do_stop()

    def onecmd_define_variable(self, args):
        """Handles the define_variable command"""
        try:
            variable_name, *value = args.split('=')
            variable_name = variable_name.strip()
            value = '='.join(value).strip()

            # Save the variable in the dictionary
            self.variables[variable_name] = value
        except ValueError as e:
            print(f"ERROR: {e}")

    def _send(self, path, value):
        try:
            OSC.sendMsg(path, value, "localhost", 9999)
        except Exception as e:
            print(f"ERROR: {_format_exception_message(e)}")

    def do_start(self, args=None):
        """Starts sequencer"""
        try:
            self._send("/start", 1)
            if self.tempo > 0:
                self.bar_duration = (60 / self.tempo) * 4 
            else:
                print("ERROR: Tempo should be greater than zero.")
                raise ValueError()
        except Exception as e:
            print(f"ERROR: {_format_exception_message(e)}")

    def do_stop(self, args=None):
        """Stops sequencer"""           
        try:
            self._send("/master_vol", 0)
            intervals = '0 0 0 0 0 0 0 0 0 0 0 0'       
            self._send("/noise", {"values": [intervals, 0, 0, 0, 0, 0, 0, 0]})
            self._send("/triangle", {"values": [intervals, 0, 0, 0, 0]})
            self._send("/square1", {"values": [intervals, 0, 0, 0, 0]})
            self._send("/square2", {"values": [intervals, 0, 0, 0, 0]})
            self._send("/triangle", {"values": [0,intervals]})
            self._send("/square1", {"values": [0, intervals]})
            self._send("/square2", {"values": [0, intervals]})
            self._send("/stop", 0)
        except Exception as e:
            print(f"ERROR: {_format_exception_message(e)}, program is terminated")
            raise ValueError()


    def do_tempo(self, args):
        """
        Changes the sequencer tempo in beats per minute

        Example: tempo 120
        """
        try:
            self.tempo = float(args)
            if self.tempo > 0:
                self.bar_duration = (60 / self.tempo) * 4
                self._send("/tempo", self.tempo*2) 
            else:
                print("ERROR: Tempo should be greater than zero.")
                return
            
        except ValueError:
            print("ERROR: tempo should be a number")

    def do_master_vol(self, args):
        """
        Sets the master volume from 0 to 1
        
        Example: master_vol 0.3
        """
        try:
            master = float(args)
            if master < 0 or master > 1:
                print("ERROR: master volume should be between 0 and 1")
                return
            else:
                self._send("/master_vol", master)
        except ValueError:
            print("ERROR: master volume should be a number")

    def play_bar(self, args):
        try:
            parts = args.split()
            if parts[0] == 'noise':
                _, vol, binary_pattern, filter_, cut_off, A, D, S, R = parts
                self.vol = float(vol)
                self.cut_off = float(cut_off)                     
                channel = "noise"
                self.A, self.D, self.S, self.R = map(int, [A, D, S, R])

                if channel.lower() in self.channels:
                    self.current_channel = self.channels[channel.lower()]
                else:
                    print(f"ERROR: Invalid oscillator name: {channel}. Available options are {', '.join(self.channels.keys())}.") 
                    return

                if filter_ == "0":
                    self.filter_string = "1 0 0"
                elif filter_ == "hp":
                    self.filter_string = "0 0 1"
                elif filter_ == "lp":
                    self.filter_string = "0 1 0"
                else:
                    print("ERROR: invalid filter name. Available options are 0, lp, hp.")
                    return

                if not (0 <= self.vol <= 1):
                    print("ERROR: volume must be in the range of 0 to 1.")
                    return

                if not (0 <= self.A <= 1000) or not (0 <= self.D <= 1000) or not (0 <= self.S <= 1000) or not (0 <= self.R <= 1000):
                    print("ERROR: A, D, S, R must be in the range of 0 to 1000.")
                    return

            if parts[0] == 'triangle' or parts[0] == 'square1' or parts[0] == 'square2':
                channel, vol, binary_pattern, note, length, duty_cycle = parts

                self.duty_cycle = float(duty_cycle)
                self.length = int(length)
                self.vol = float(vol)

                if channel.lower() in self.channels:
                    self.current_channel = self.channels[channel.lower()]
                else:
                    print(f"ERROR: Invalid oscillator name: {channel}. Available options are {', '.join(self.channels.keys())}.") 
                    return

                if not (0 <= self.duty_cycle <= 1):
                    print("ERROR: Duty cycle must be in the range of 0 to 1.")
                    return

                if not (1 <= self.length <= 4):
                    print("ERROR: Length must be in the range of 1 to 4.")
                    return

                if not (0 <= self.vol <= 1):
                    print("ERROR: Volume must be in the range of 0 to 1.")
                    return

                if "triangle" in self.current_channel:
                    if self.duty_cycle != 0:
                        print("ERROR: Duty cycle is not applicable to the 'triangle' oscillator and should be 0.")
                        self.duty_cycle = 0

                # Convert note to MIDI note value
                self.midi_note = note_to_midi(note)
                self.duty_cycle = (self.duty_cycle-0.5)*2
            binary_list = [int(bit) for bit in binary_pattern]
            if len(binary_list) > 8:
                print("ERROR: Binary pattern should have at most 8 bits.")
                return
            else:
                # Pad the binary list to make it 8 bits long
                binary_list += [0] * (8 - len(binary_list))
                # Check if any bit is not 0 or 1
                if all(bit in {0, 1} for bit in binary_list):
                    # Convert the list to a string with spaces between each character
                    self.binary_string = ' '.join(map(str, binary_list))
                else:
                    print("ERROR: Binary pattern should only contain 0s and 1s.")
                    return

            if self.current_channel == "/noise":   
                if self.current_channel in self.oscillators:
                    self._send(self.current_channel, {"values": [self.binary_string, self.vol, self.filter_string, self.cut_off, self.A, self.D, self.S, self.R]})
                else:
                    self.oscillators.append(self.current_channel)
                    self._send(self.current_channel, {"values": [self.binary_string, self.vol, self.filter_string, self.cut_off, self.A, self.D, self.S, self.R]})
            else:    
                if self.current_channel in self.oscillators:
                    self._send(self.current_channel, {"values": [self.binary_string, self.vol, self.midi_note, self.duty_cycle, self.length]})
                else:
                    self.oscillators.append(self.current_channel)
                    self._send(self.current_channel, {"values": [self.binary_string, self.vol, self.midi_note, self.duty_cycle, self.length]})

        except ValueError as e:
            print(f"ERROR: {e}")

    def do_play(self, args):
        """
        Plays tunes or noises for multiple channels

        For noise:
            vol: Volume from 0 to 1
            binary_pattern: Pattern to set the array
            filter_: High pass, low pass or 0
            cut_off: Cut-off frequency in Hz
            A: Attack in ms
            D: Delay in ms
            S: Sustain in ms
            R: Release in ms

            Example: noise 1 10101011 hp 3000 10 50 3 50

        For square1, square2, or triangle:
            vol: Volume from 0 to 1
            binary_pattern: Pattern to set the array
            note: In English notation from c1 to c8
            length: Length in 8th from 1 to 4
            duty_cycle: Duty cycle from 0 to 1

            Example: square1 0.7 01010101 e3 1 0.2
        """

        channels_to_play = args.split(',')
        for channel in channels_to_play:
            self.play_bar(channel)

    def do_wait(self, args):
        """
        Plays the set channels and effects for a selected number of bars

        Example: wait 2
        """
        try:
            time.sleep(self.bar_duration*float(args))
        except ValueError:
            print("ERROR: Invalid duration for waiting")

    def do_pause(self, args):
        """
        Pauses selected channels
        
        Example: pause noise,square1
        """
        try:
            channels_to_pause = args.split(',')
            for channel in channels_to_pause:
                parts = channel.split()
                intervals = '0 0 0 0 0 0 0 0 0 0 0 0' 
                if parts[0] == 'noise':
                    self._send("/noise", {"values": [intervals, 0, 0, 0, 0, 0, 0, 0]})
                elif parts[0] == 'triangle':
                    self._send("/triangle", {"values": [intervals, 0, 0, 0, 0]})
                elif parts[0] == 'square1':
                    self._send("/square1", {"values": [intervals, 0, 0, 0, 0]})
                elif parts[0] == 'square2':
                    self._send("/square2", {"values": [intervals, 0, 0, 0, 0]})
        except ValueError as e:
            print(f"ERROR: {e}")

    def do_set_effect(self, args):
        """
        Sets the arpeggio effect

        channel: Channel you want to set
        cycle_steps: Modulo value from 1 to 12
        intervals: P1 m2 M2 m3 M3 P4 A4 d5 P5 m6 M6 m7 M7 P8

        Example: set_effect square1 3 P1M3P4
        """
        try:
            parts = args.split()
            if len(parts) == 3:
                channel, cycle_steps, intervals = parts
                cycle_steps = int(cycle_steps)
                intervals = str(intervals)
            else:
                print("ERROR: Invalid number of arguments for 'set_effect' command.")
                return

            if channel.lower() in self.channels:
                self.current_channel = self.channels[channel.lower()]
            else:
                print(f"ERROR: Invalid oscillator name: {channel}. Available options are {', '.join(self.channels.keys())}.")
                return

            if not 0 <= cycle_steps <= 12:
                print("ERROR: Modulo must be in the range of 0 to 12.")
                return

            interval_pairs = [intervals[i:i+2] for i in range(0, len(intervals), 2)]
            semitones = intervals_to_semitones(interval_pairs)
            if not all(isinstance(interval, (int, float)) for interval in semitones):
                return
            if len(semitones) > 12:
                print("ERROR: Semitones should have at most 12 intervals.")
                return
            else:
                semitones += [0] * (12 - len(semitones))
                if all(isinstance(semitone, int) for semitone in semitones):
                    semitones = ' '.join(map(str, semitones))
                else:
                    print("ERROR: Semitones should be integers.")
                    return
                self._send(self.current_channel, {"values": [cycle_steps, semitones]})
        except ValueError as e:
            print(f"ERROR: {e}")

    def do_stop_effect(self, args):
        """
        Stops the arpeggio effect

        Example: stop_effect square1
        """
        try:
            channel = args
            if channel.lower() in self.channels:
                self.current_channel = self.channels[channel.lower()]
            else:
                print(f"ERROR: Invalid oscillator name: {channel}. Available options are {', '.join(self.channels.keys())}.")
                return
            cycle_steps = 0
            intervals = '0 0 0 0 0 0 0 0 0 0 0 0'
            self._send(self.current_channel, {"values": [cycle_steps, intervals]})
        except ValueError as e:
            print(f"ERROR: {e}")

def note_to_midi(note):
    """Converts note to midi value"""
    note_mapping = {
        'c': 0, 'c#': 1, 'db': 1, 'd': 2, 'd#': 3, 'eb': 3,
        'e': 4, 'f': 5, 'f#': 6, 'gb': 6, 'g': 7, 'g#': 8,
        'ab': 8, 'a': 9, 'a#': 10, 'bb': 10, 'b': 11
    }

    try:
        note_name, octave = note[:-1].lower(), int(note[-1])

        if note_name in note_mapping:
            if 1 <= octave <= 8:
                midi_note = note_mapping[note_name] + (octave) * 12 + 12
                return midi_note
            else:
                print(f"ERROR: Invalid octave: {octave}, must be in the range of c1 to c8")
        else:
            print(f"ERROR: Invalid note name: {note_name}")
            return None

    except (KeyError, ValueError) as e:
        print(f"ERROR: {_format_exception_message(e)}")
        return None

def intervals_to_semitones(interval_sequence):
    """Converts intervals to semitones"""
    interval_dict = {
        'P1': 0, 'm2': 1, 'M2': 2, 'm3': 3, 'M3': 4,
        'P4': 5, 'A4': 6, 'd5': 6, 'P5': 7, 'm6': 8,
        'M6': 9, 'm7': 10, 'M7': 11, 'P8': 12
    }
    semitones = []
    for interval in interval_sequence:
        if interval in interval_dict:
            semitones.append(interval_dict[interval])
        else:
            print(f"ERROR: Invalid interval: {interval}")
            return None

    return semitones

def main():
    b = BitBeats()
    try:
        b.cmdloop()
    except KeyboardInterrupt:
        print("KeyboardInterrupt: Stopping the script.")
        return
    except Exception as e:
        print(f"ERROR: {_format_exception_message(e)}")

def _format_exception_message(exception):
    return f"{type(exception).__name__}: {str(exception)}"

if __name__ == "__main__":
    main()
