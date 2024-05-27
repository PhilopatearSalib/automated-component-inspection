#!/bin/bash


if [ $# -ne 1]; then
	echo "Usage: $0 <object number>"
	exit 1
fi

obj_num=$1

while true
do

	for i in $(seq 1 1 100)
	do

		#Camera fixed on Rx0
		i2cset -y 10 0x24 0x24 0x02
		libcamera-still -o BadImages/Obj${obj_num}_Or${i}_bad_face1.jpg --autofocus-mode manual --lens-position 8
                echo "Captured obj ${obj_num} face1 oriantation ${i}"

		#Camera fixed on Rx1
		i2cset -y 10 0x24 0x24 0x12
		libcamera-still -o BadImages/Obj${obj_num}_Or${i}_bad_face2.jpg --autofocus-mode manual --lens-position 7
	        echo "Captured obj ${obj_num} face2 oriantation ${i} "

		#Camera fixed on Rx2
		i2cset -y 10 0x24 0x24 0x22
		libcamera-still -o BadImages/Obj${obj_num}_Or${i}_bad_face3.jpg --autofocus-mode manual --lens-position 7
        	echo "Captured Obj ${obj_num} face3 oriantation ${i} "

		#Camera fixed on Rx3
		i2cset -y 10 0x24 0x24 0x32
		libcamera-still -o BadImages/Obj${obj_num}_Or${i}_bad_face4.jpg --autofocus-mode manual --lens-position 8
        	echo "Captured obj ${obj_num} face4 oriantation ${i}"	

		while true; do

			read -p "Do you want to continue? [Y/N]: " answer 
			case $answer in
				[Yy]* ) break;;
				[Nn]* ) echo "Exitting" ; exit;;
				* ) echo "please answer yes or no." ;;
			esac
		done
	done
done

