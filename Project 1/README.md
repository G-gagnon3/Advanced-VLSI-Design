# Project 1: FIR Filter

## Introduction
The goal of this project was to design and implement a 100+ tap low-pass FIR filter which achieved a stop band attenuation of 80 dB with a transition region between 0.2 and 0.23. After designing the filter, considerations needed to be made into pipelining and parallelization

To allow for rapid development and flexibility, I decided to base this project around a custom-made high-level synthesis tool. With this tool, I could export a filter specification from Matlab and synthesize a SystemVerilog file which itself could then be synthesized in Design Compiler

## Filter Generation

To generate the filter, I make use of the "firpm" function included in Matlab as it includes the ability to specify a transition band and specific amplitudes for bands. I used the function as follows:
```
taps = firpm(tap_quantity, [0 lower_cutoff upper_cutoff 1], [1 1 0 0]);
```
Alternatively, if you wanted it to optimize to reach the exact stopband attenuation, you could use the following in place of 0.
```
cutoff_amp = db2mag(-80);
```

After generation, I apply 3 quantizations (4, 8, and 16 bit) to the taps. Then, I de-quantize the taps and compare their responses on a multiplot.

## HLS Tool

The HLS tool is relatively simple in nature. It was written in Python and uses a block structure like standard SystemVerilog. The methodology is that blocks are generated, built, collapsed, then placed into higher-level blocks. For example, lines are inserted into an if block which then gets inserted into a module block.

The functionality is limited only to what I needed for the FIR filter, but it certainly could be expanded to include more blocks, like case statements. 

For the actual design of the filter, both 1 parallel designs use a setup where the input is delayed before being multiplied with a long adder tree. A systolic structure could have been used, but I did not feel that gave enough latitude on the design space exploration. For the parallel design, I had noticed that although the inputs could not be delayed in the same way that the 1-parallel designs could, they could be pipelined as long as they obeyed the same structure as if there were n taps (See included diagram). With this adjustment, it could again be delayed in the same way.

## Design Compiler

For Design Compiler, I used the shell and a script I've used for research to compile, synthesize, optimize, and evaluate the design. Additionally, because of its availability, I chose to use FreePDK45 as my library. 

### Analyses + Configuration:

For the purposes of analyses, I set the clock rate at 1 GHz unless otherwise specified. This is mainly to simplify the process and get baselines. When attempting to maximize speed, I bring the clock rate up to force optimization. For power, I set the switching rates of all signals (except reset) to the maximum (0.5 static, 1 dynamic) to try to get an upper bound.

### Side Notes:
A note about FreePDK45 and other versions of it. While they do exist for newer processes (15nm and 3nm), they do not come precompiled for Design Compiler. This would not be much of an issue if we had the tools to compile them, but we don't. Library Compiler is outdated and requires a dependency not on the server, so I can't use that, and I do not believe we have Custom Compiler either. 

## Usage

For Matlab, use the provided script. Adjustable parameters are placed the top of the file. As it is currently will generate the taps used. Additionally, the json file is provided so you do not need to run Matlab.

For the HLS tool, using the notebook is the best way to run it, as it has included documentation.

For Design Compiler, the script I used is included. As well, FreePDK45 can be downloaded [here](https://eda.ncsu.edu/freepdk/freepdk45/). Using the script can be done with 

`dc_shell-t -f path/to/FIR.tcl`

If design compiler is not yet in your path, the following lines will add it. These should be placed in .bashrc so they are always set.

```
export DC_HOME="/cad/synopsys/syn/P-2019.03-SP4/"
export PATH="$DC_HOME/bin:$PATH"
```

## Results

### Filter Quality
For filter quantization, the loss in fidelity was severe when moving from a 

### Hardware Implementation
I cannot tell if it is Design Compiler optimizing the design well or FreePDK45 having limited timing information, but surprisingly the direct design had the greatest slack of all the designs. I am not entirely sure why, but that was the synthesis result. Also, unsurprisingly it was the smallest of the synthesized designs. All reports are included in the repo, but they are summarized below

| Design | 1 GHz Slack |    Area    | Static Power (uW) | Dynamic Power (mW) |
| ----------- | ----------- | ----------- | ----------- | ----------- |
| Direct | 0.82        | 67785.69 | 709.5 | 150.2 |
| Pipelined | 0.50 | 69078.14 | 716.6 | 152.9 |
| 2-Parallel | 0.82 | 264476.8 | 1,063 | 1.21 |
| 3-Parallel | 0.82 | 22743.68 | 238.0| 51.08 |

With the parallel designs, the results were a bit surprising. This most likely is due to a semantic bug which led to drastic optimizations. However, the slack value lines up with that of the Direct design, which makes sense.

There were also many violators, but those all had tolerances below the significant figure range, so I was unable to determine how close they were to being met.

## Conclusion

Overall, the project was a success. I was able to design and implement an FIR filter to the required specifications. I would have preferred to see a much better quantization of 4-Bits since many neural networks have been able to operate with that degree of precision. The generated designs were able to meet required constraints and were able to be optimized further.

### Filter Design
There is certainly a lot more which could be done to make the filter more efficient. I found that while a smaller tap count could not achieve a full 80 dB attenuation, they could get close. Further, these filters quantized very well. Additionally, the underlying optimizer is **quantization unaware** meaning that it fails to consider the effects of quantization error. An ideal aware optimizer would factor in the outside constraint and likely vastly improve the quantization. 

If I was to design a filter to implement with a precision constraint, I would look to either build off of someone else's attempt at quantization aware design first. If there were none to evaluate/learn from, I would start by attempting a multi-level FIR filter. The concept here is that the first filter will attempt to cover the majority of the goals, and then a second could be used to "clean up" the remaining portion of the frequency response. Mathematically, these filters may be able to be condensed down or parallelized since they are LTI, but I am not sure.

### HLS Tool
The HLS tool was good as a proof of concept and I definitely learned a lot from it. Things like this are helpful for prototyping and power estimation, especially when the scope of synthesis is small. Where I often am limited in research projects is my ability to explore the design space. A tool like this would help me to design architectures quickly while getting reasonable power values. Often I find that existing tools do not do *exactly* what I need them to do, making them somewhat useless since I need the most accurate result I can get. Combining an HLS tool with a simulator could be a very powerful prototyping tool for architecture evaluation. 

Assuming the IO remains identical, a workflow which could do power, performance, area (PPA) analysis would be 
1. HLS: SystemVerilog 
2. Design Compiler: Power & Area 
3. CocoTB: Cycle-accurate simulation

This is something I may look to develop myself for my own personal/group research tools. I think I would choose to design multiple flexible modules with it, but not up to system-level as that would require strong dependency mapping.


