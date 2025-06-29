## voltpeek
voltpeek is a command based PC oscilloscope software. voltpeek works
with the NS1 headless oscilloscope [hardware](https://hackaday.io/project/197104-ns1-oscilloscope) and [firmware](https://github.com/schuyler4/NS1-Firmware).

<p align="center">
<img src="./picture.png" width=400>
</p>

### Command Based 
By command based, we mean that everything in voltpeek is controlled and adjusted via command instead of
click and drag or text entry like many other oscilloscope softwares that run on PC. For example, the
scale command will put the oscilloscope/software in adjustment mode. The horizontal and vertical
scales can then be adjusted using the `h`, `j`, `k`, and `l` keys. `ctrl-c` or `esc` will put the software back into 
command mode. As may be obvious, this is inspired by the Vim text editor. 

### Installation
Install from source:

`git clone https://github.com/schuyler4/voltpeek.git`  
`python3 -m pip install -e voltpeek`