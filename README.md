# BitBeats

#Introduction:

BitBeats is a computer music language specifically designed to create authentic beats in the style of early 1980s chiptune music. The language is implemented by a Python interpreter that allows a PureData patch to be controlled as a synthesizer and sequencer via a command line. BitBeats provides functions to control four channels: a triangle signal generator, two square wave signal generators and a noise channel generator. Each channel can be configured individually, including parameters such as volume, pitch and various effects such as arpeggio. Skillful combinations of these channels create beats with the characteristic sound of chiptune music. The future development of BitBeats aims to continuously expand the functionality of the system. The aim is to provide users with a tool with which they can create chiptune music as easily as possible.

#Required modules in Python:

Make sure that you have installed Python version 3.7 or higher.

'OSC' from https://opensoundcontrol.stanford.edu/spec-1_0.html

'cmd' from https://github.com/python/cpython/blob/3.12/Lib/cmd.py

#Required externals in PureData:

'zexy' from https://git.iem.at/pd/zexy

#Executing the program via the command prompt:

Make sure that you opened the PureData patch 'BitBeats.pd' and activated the audio output there.

To start BitBeats via the command prompt 'CMD', you should first ensure that the command line is located in the directory with the Python file 'BitBeats.py'. This can be changed with the command 'cd path\to\folder', replacing 'path\to\folder' with the corresponding path. The commands can also be entered directly if the program was started using the command 'python BitBeats.py' to start the programm and enable live processing. Alternatively, the program can be started using the command 'python BitBeats.py run_script commands.txt'. The file 'commands.txt' contains the commands that the program should execute.

#Documentation:

Documentation of all commands and sample code can be found in design.pdf.

#License:
Copyright (C) 2024 Hannes PESCOLLER, Eugen-Maximilian STANGL

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/

