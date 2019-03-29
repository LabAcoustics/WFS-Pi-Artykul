#!/usr/bin/env python3
import nptdms as nt
import numpy as np
from glob import glob
import matplotlib.pyplot as ppl
import matplotlib
import locale
import platform

matplotlib.use("pgf")

if platform.system() == 'Windows':
    locale.setlocale(locale.LC_NUMERIC, 'Polish')
else:
    locale.setlocale(locale.LC_NUMERIC, ('pl_PL', 'UTF-8'))

mic_dist = 0.4
p0 = 2 * 10**(-5)
q = 10

s = 5
f = 200

sig = f"sin{f}_s{s}"
print(f"Plotting {sig}...")

file1 = nt.TdmsFile(glob(f"pozycja_mik1/{sig}*.tdms")[0])
file2 = nt.TdmsFile(glob(f"pozycja_mik2/{sig}*.tdms")[0])

ref1 = file1.object("PXI1Slot3", "PXI1Slot3/ai0")

clock1 = file1.object("PXI1Slot4", "PXI1Slot4/ai0")
clock2 = file2.object("PXI1Slot4", "PXI1Slot4/ai0")

c1_start = next(x[0] for x in enumerate(clock1.data) if x[1] > 0.3)
c2_start = next(x[0] for x in enumerate(clock2.data) if x[1] > 0.3)

tdiff = clock1.time_track()[c1_start] - clock2.time_track()[c2_start]

siglen = len(ref1.data)
fs = int(1/ref1.time_track()[1])
t = ref1.time_track()

newlen = siglen//q
newfs = fs//q

matrix1 = np.zeros(16)
matrix2 = np.zeros(16)

t1 = c1_start+fs*10
t2 = int(round(t1 - fs*tdiff))

mean_s = 1

for it in range(8):
    matrix1[it] = np.mean(
        file1.object('PXI1Slot2', f"PXI1Slot2/ai{it}")
        .data[t1-mean_s:t1+mean_s])
    matrix1[it+8] = np.mean(
        file1.object('PXI1Slot6', f"PXI1Slot6/ai{it}")
        .data[t1-mean_s:t1+mean_s])
    matrix2[it] = np.mean(
        file2.object('PXI1Slot2', f"PXI1Slot2/ai{it}")
        .data[t2-mean_s:t2+mean_s])
    matrix2[it+8] = np.mean(
        file2.object('PXI1Slot6', f"PXI1Slot6/ai{it}")
        .data[t2-mean_s:t2+mean_s])

matrix = np.hstack((matrix1.reshape(4, 4), matrix2.reshape(4, 4)))
x = np.arange(0, 8)
y = np.arange(0, 4)

ppl.figure(figsize=(3.5, 1.5))
ppl.imshow(matrix, interpolation="spline16", cmap='jet', vmin=0.0,
           vmax=0.15, extent=(-mic_dist*3.5, mic_dist*3.5, mic_dist*3, 0))
ppl.tick_params(direction="in", width=0.2)
cbar = ppl.colorbar()
cbar.ax.tick_params(direction="in", width=0.2, length=1)
cbar.ax.set_title(r"Ciśnienie ak. [\si{\pascal}]", fontsize=8)

ppl.xlabel(r"x [\si{\meter}]")
ppl.ylabel(r"y [\si{\meter}]")
ppl.xticks(np.arange(-1, 1.5, step=0.5),
           ('-1,0', '-0,5', '0,0', '0,5', '1,0'))
ppl.yticks(np.arange(1.2, -0.2, step=-0.2),
           ('1,2', '1,0', '0,8', '0,6', '0,4', '0,2', '0,0'))
ppl.grid(False)
ppl.savefig(f"plots/{sig}_IAB.pgf")
ppl.close()
