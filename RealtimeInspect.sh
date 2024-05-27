#!/bin/bash

for i in $(seq 8 1 8)
do
#Camera fixed on Rx0
i2cset -y 10 0x24 0x24 0x02
libcamera-still -o Realtime/Obj1_Or9_bad_f1_Position$i.jpg --autofocus-mode manual --lens-position $i
        echo "Face1 Position $i"

#Camera fixed on Rx3
i2cset -y 10 0x24 0x24 0x32
libcamera-still -o Realtime/Obj1_Or9_bad_f4_Position$i.jpg --autofocus-mode manual --lens-position $i
        echo "Face4 Position $i"
done 

for i in $(seq 9 1 9)
do

#Camera fixed on Rx1
i2cset -y 10 0x24 0x24 0x12
libcamera-still -o Realtime/Obj1_Or9_bad_f2_Position$i.jpg --autofocus-mode manual --lens-position $i
       echo "Face2 Position $i"

#Camera fixed on Rx2
i2cset -y 10 0x24 0x24 0x22
libcamera-still -o Realtime/Obj1_Or9_bad_f3_Position$i.jpg --autofocus-mode manual --lens-position $i
        echo "Face3 Position $i"

done

python3 Realtime_Inspection.py
