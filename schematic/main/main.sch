EESchema Schematic File Version 4
LIBS:main-cache
EELAYER 26 0
EELAYER END
$Descr USLetter 11000 8500
encoding utf-8
Sheet 1 1
Title "Barbot Main Controller"
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L teensy_32:Teensy_32 A2
U 1 1 5BCF8052
P 7700 2600
F 0 "A2" H 7350 3550 50  0000 C CNN
F 1 "Teensy_32" H 8100 3550 50  0000 C CNN
F 2 "teensy_32:teensy_32" H 8000 1550 50  0001 L CNN
F 3 "https://www.pjrc.com/teensy/teensy31.html" H 7500 3650 50  0001 C CNN
	1    7700 2600
	1    0    0    -1  
$EndComp
$Comp
L arduino_pro_mini:Arduino_Pro_Mini A1
U 1 1 5BCF80B6
P 3300 2600
F 0 "A1" H 2950 3550 50  0000 C CNN
F 1 "Arduino_Pro_Mini" H 3850 3550 50  0000 C CNN
F 2 "arduino_pro_mini:arduino_pro_mini" H 3450 1550 50  0001 L CNN
F 3 "https://store.arduino.cc/usa/arduino-pro-mini" H 3100 3650 50  0001 C CNN
	1    3300 2600
	1    0    0    -1  
$EndComp
$Comp
L main-rescue:Conn_01x03_Male-Connector-main-rescue J3
U 1 1 5BCF834E
P 1150 2650
F 0 "J3" H 1256 2928 50  0000 C CNN
F 1 "Sensor1" H 1256 2837 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x03_Pitch2.54mm" H 1150 2650 50  0001 C CNN
F 3 "~" H 1150 2650 50  0001 C CNN
	1    1150 2650
	1    0    0    -1  
$EndComp
$Comp
L main-rescue:Conn_01x02_Male-Connector-main-rescue J7
U 1 1 5BCF83FD
P 1150 4500
F 0 "J7" H 1256 4678 50  0000 C CNN
F 1 "Button" H 1256 4587 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x02_Pitch2.54mm" H 1150 4500 50  0001 C CNN
F 3 "~" H 1150 4500 50  0001 C CNN
	1    1150 4500
	1    0    0    -1  
$EndComp
$Comp
L main-rescue:Conn_01x03_Male-Connector-main-rescue J4
U 1 1 5BCF8720
P 1150 3150
F 0 "J4" H 1256 3428 50  0000 C CNN
F 1 "Relay0" H 1256 3337 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x03_Pitch2.54mm" H 1150 3150 50  0001 C CNN
F 3 "~" H 1150 3150 50  0001 C CNN
	1    1150 3150
	1    0    0    -1  
$EndComp
$Comp
L main-rescue:Conn_01x03_Male-Connector-main-rescue J5
U 1 1 5BCF8793
P 1150 3600
F 0 "J5" H 1256 3878 50  0000 C CNN
F 1 "Relay1" H 1256 3787 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x03_Pitch2.54mm" H 1150 3600 50  0001 C CNN
F 3 "~" H 1150 3600 50  0001 C CNN
	1    1150 3600
	1    0    0    -1  
$EndComp
$Comp
L logic_level_converter:LLC4 M1
U 1 1 5BCF9780
P 5000 2150
F 0 "M1" H 4750 2550 50  0000 C CNN
F 1 "LLC4" H 5250 2550 50  0000 C CNN
F 2 "logic_level_converter:LLC4" H 5300 1750 50  0001 C CNN
F 3 "" H 5000 2050 50  0001 C CNN
	1    5000 2150
	1    0    0    -1  
$EndComp
$Comp
L main-rescue:R_US-Device-main-rescue R1
U 1 1 5BCF9849
P 2350 1900
F 0 "R1" V 2550 1900 50  0000 C CNN
F 1 "330" V 2450 1900 50  0000 C CNN
F 2 "Resistors_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical" V 2390 1890 50  0001 C CNN
F 3 "~" H 2350 1900 50  0001 C CNN
	1    2350 1900
	1    0    0    -1  
$EndComp
$Comp
L main-rescue:CP1-Device-main-rescue C1
U 1 1 5BCF98F0
P 4200 3000
F 0 "C1" H 4315 3046 50  0000 L CNN
F 1 "1000u" H 4315 2955 50  0000 L CNN
F 2 "Capacitors_THT:CP_Radial_D10.0mm_P5.00mm" H 4200 3000 50  0001 C CNN
F 3 "~" H 4200 3000 50  0001 C CNN
	1    4200 3000
	1    0    0    -1  
$EndComp
NoConn ~ 3400 1600
NoConn ~ 3800 2000
NoConn ~ 3800 2100
NoConn ~ 3800 2800
NoConn ~ 3800 2900
NoConn ~ 3800 3000
NoConn ~ 3800 3100
NoConn ~ 3800 3200
NoConn ~ 3800 3300
Wire Wire Line
	1350 900  1750 900 
Wire Wire Line
	3200 900  3200 1500
Wire Wire Line
	3200 3800 3200 3700
Wire Wire Line
	3200 3800 3400 3800
Wire Wire Line
	3400 3800 3400 3700
NoConn ~ 2800 3300
NoConn ~ 2800 2900
NoConn ~ 2800 3000
NoConn ~ 2800 3100
NoConn ~ 2800 3200
NoConn ~ 3800 2550
NoConn ~ 3800 2450
NoConn ~ 3800 2350
NoConn ~ 3800 2250
Connection ~ 3200 3800
$Comp
L main-rescue:Conn_01x03_Male-Connector-main-rescue J1
U 1 1 5BCFDB4F
P 1150 1700
F 0 "J1" H 1256 1978 50  0000 C CNN
F 1 "LEDs" H 1256 1887 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x03_Pitch2.54mm" H 1150 1700 50  0001 C CNN
F 3 "~" H 1150 1700 50  0001 C CNN
	1    1150 1700
	1    0    0    -1  
$EndComp
Wire Wire Line
	1350 1200 1650 1200
Wire Wire Line
	1550 7000 1350 7000
Wire Wire Line
	1350 2650 1650 2650
Connection ~ 1750 900 
Wire Wire Line
	1750 900  2500 900 
Connection ~ 1550 7000
Wire Wire Line
	2800 2100 2600 2100
Wire Wire Line
	2600 2100 2600 1300
Wire Wire Line
	2600 1300 4400 1300
Wire Wire Line
	2800 2000 2700 2000
Wire Wire Line
	2700 2000 2700 1400
Wire Wire Line
	2700 1400 4300 1400
Wire Wire Line
	5050 1700 5050 1500
Wire Wire Line
	5050 1500 6000 1500
Wire Wire Line
	7800 1500 7800 1600
Wire Wire Line
	4950 2700 5050 2700
Wire Wire Line
	5050 2700 5050 2600
Connection ~ 4950 2700
Wire Wire Line
	4950 2700 4950 2600
NoConn ~ 7800 3700
Wire Wire Line
	7200 2900 6800 2900
Wire Wire Line
	7200 2800 6700 2800
Wire Wire Line
	7200 2700 6600 2700
Wire Wire Line
	7200 2600 6500 2600
Wire Wire Line
	7200 2500 6400 2500
Wire Wire Line
	6400 2500 6400 5350
Wire Wire Line
	7200 2400 6300 2400
Wire Wire Line
	6300 2400 6300 5250
Wire Wire Line
	7200 2300 6200 2300
Wire Wire Line
	6200 2300 6200 5150
Wire Wire Line
	7200 2200 6100 2200
Wire Wire Line
	6100 2200 6100 5050
NoConn ~ 8200 3000
NoConn ~ 8200 3100
NoConn ~ 8200 3200
NoConn ~ 8200 3300
Wire Wire Line
	5500 5100 5500 4400
$Comp
L main-rescue:PWR_FLAG-power-main-rescue #FLG0101
U 1 1 5BE4B784
P 2850 7000
F 0 "#FLG0101" H 2850 7075 50  0001 C CNN
F 1 "PWR_FLAG" H 2850 7174 50  0000 C CNN
F 2 "" H 2850 7000 50  0001 C CNN
F 3 "~" H 2850 7000 50  0001 C CNN
	1    2850 7000
	1    0    0    -1  
$EndComp
Connection ~ 2850 7000
Wire Wire Line
	2850 7000 3200 7000
$Comp
L main-rescue:PWR_FLAG-power-main-rescue #FLG0102
U 1 1 5BE4B7FF
P 2500 1200
F 0 "#FLG0102" H 2500 1275 50  0001 C CNN
F 1 "PWR_FLAG" H 2500 1374 50  0000 C CNN
F 2 "" H 2500 1200 50  0001 C CNN
F 3 "~" H 2500 1200 50  0001 C CNN
	1    2500 1200
	1    0    0    -1  
$EndComp
$Comp
L main-rescue:PWR_FLAG-power-main-rescue #FLG0103
U 1 1 5BE4B85A
P 2500 900
F 0 "#FLG0103" H 2500 975 50  0001 C CNN
F 1 "PWR_FLAG" H 2500 1074 50  0000 C CNN
F 2 "" H 2500 900 50  0001 C CNN
F 3 "~" H 2500 900 50  0001 C CNN
	1    2500 900 
	1    0    0    -1  
$EndComp
Connection ~ 2500 900 
Wire Wire Line
	2500 900  3200 900 
Wire Wire Line
	4950 2700 4950 3800
Wire Wire Line
	7600 3700 7600 3800
Wire Wire Line
	7600 3800 7700 3800
Wire Wire Line
	7700 3800 7700 3700
Wire Wire Line
	7600 3800 4950 3800
Connection ~ 7600 3800
Connection ~ 4950 3800
Text Label 2000 900  0    50   ~ 0
5V
Text Label 2000 1200 0    50   ~ 0
5VS
Text Label 1800 7000 0    50   ~ 0
GND
Text Label 1850 5100 0    50   ~ 0
24VS
Text Label 2350 2600 2    50   ~ 0
D6
Text Label 2350 2500 2    50   ~ 0
D5
Text Label 2150 2400 2    50   ~ 0
D4
Text Label 2150 2300 2    50   ~ 0
D3
Text Label 2100 1700 2    50   ~ 0
D2
Text Label 3500 1300 2    50   ~ 0
A1_D1
Text Label 3500 1400 2    50   ~ 0
A1_D0
Text Label 5850 2000 2    50   ~ 0
A2_D0
Text Label 5850 2100 2    50   ~ 0
A2_D1
Text Label 6750 1500 2    50   ~ 0
3.3V
Text Label 9200 2900 0    50   ~ 0
P0
Text Label 9100 2800 0    50   ~ 0
P1
Text Label 9000 2700 0    50   ~ 0
P2
Text Label 8900 2600 0    50   ~ 0
P3
Text Label 8800 2500 0    50   ~ 0
P4
Text Label 8700 2400 0    50   ~ 0
P5
Text Label 8600 2300 0    50   ~ 0
P6
Text Label 8500 2200 0    50   ~ 0
P7
Text Label 6800 2900 2    50   ~ 0
P8
Text Label 6700 2800 2    50   ~ 0
P9
Text Label 6600 2700 2    50   ~ 0
P10
Text Label 6500 2600 2    50   ~ 0
P11
Text Label 6400 2500 2    50   ~ 0
P12
Text Label 6300 2400 2    50   ~ 0
P13
Text Label 6200 2300 2    50   ~ 0
P14
Text Label 6100 2200 2    50   ~ 0
P15
Text Label 7200 3100 2    50   ~ 0
~ENABLE
Text Label 7000 3000 2    50   ~ 0
DIR
$Comp
L main-rescue:Conn_01x02_Male-Connector-main-rescue J8
U 1 1 5BE5E3EF
P 1150 5500
F 0 "J8" H 1256 5678 50  0000 C CNN
F 1 "5VS" H 1256 5587 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x02_Pitch2.54mm" H 1150 5500 50  0001 C CNN
F 3 "~" H 1150 5500 50  0001 C CNN
	1    1150 5500
	1    0    0    -1  
$EndComp
Wire Wire Line
	4950 7000 4200 7000
Connection ~ 3200 7000
Wire Wire Line
	5950 4850 7450 4850
Wire Wire Line
	7450 4850 7450 6150
Connection ~ 7450 4850
Wire Wire Line
	7450 4850 9350 4850
Wire Wire Line
	4950 3800 4950 6500
Wire Wire Line
	7600 6500 4950 6500
Connection ~ 4950 6500
Wire Wire Line
	4950 6500 4950 7000
Wire Wire Line
	7450 4850 7450 4400
Wire Wire Line
	7450 4400 5500 4400
Wire Wire Line
	5950 5050 6100 5050
Wire Wire Line
	5950 5150 6200 5150
Wire Wire Line
	5950 5250 6300 5250
Wire Wire Line
	5950 5350 6400 5350
$Comp
L main-rescue:Conn_01x15_Male-Connector-main-rescue CON2
U 1 1 5BCFD97B
P 5750 5550
F 0 "CON2" H 5850 6400 50  0000 C CNN
F 1 "Right" H 5850 4750 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Angled_1x15_Pitch2.54mm" H 5750 5550 50  0001 C CNN
F 3 "~" H 5750 5550 50  0001 C CNN
	1    5750 5550
	1    0    0    1   
$EndComp
$Comp
L main-rescue:Conn_01x15_Male-Connector-main-rescue CON1
U 1 1 5BCFD9D4
P 9550 5550
F 0 "CON1" H 9650 6400 50  0000 C CNN
F 1 "Left" H 9650 4750 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Angled_1x15_Pitch2.54mm" H 9550 5550 50  0001 C CNN
F 3 "~" H 9550 5550 50  0001 C CNN
	1    9550 5550
	-1   0    0    -1  
$EndComp
Wire Wire Line
	5950 6250 7450 6250
Wire Wire Line
	7450 6150 7450 6250
Connection ~ 7450 6250
Wire Wire Line
	7450 6250 9350 6250
Wire Wire Line
	5950 6150 7600 6150
Wire Wire Line
	5950 4950 7600 4950
Wire Wire Line
	7600 6500 7600 6150
Connection ~ 7600 6150
Wire Wire Line
	7600 6150 9350 6150
Wire Wire Line
	6800 6050 5950 6050
Wire Wire Line
	6800 2900 6800 6050
Wire Wire Line
	6700 5950 5950 5950
Wire Wire Line
	6700 2800 6700 5950
Wire Wire Line
	6600 5850 5950 5850
Wire Wire Line
	6600 2700 6600 5850
Wire Wire Line
	6500 5750 5950 5750
Wire Wire Line
	6500 2600 6500 5750
Wire Wire Line
	5950 5550 7750 5550
Wire Wire Line
	7750 5550 7750 3950
Wire Wire Line
	7750 3950 6000 3950
Wire Wire Line
	6000 3950 6000 1500
Connection ~ 7750 5550
Wire Wire Line
	7750 5550 9350 5550
Connection ~ 6000 1500
Wire Wire Line
	6000 1500 7800 1500
$Comp
L main-rescue:Jumper-Device-main-rescue JP1
U 1 1 5BD13E35
P 6200 1300
F 0 "JP1" H 6200 1564 50  0000 C CNN
F 1 "PRG" H 6200 1473 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x02_Pitch2.54mm" H 6200 1300 50  0001 C CNN
F 3 "~" H 6200 1300 50  0001 C CNN
	1    6200 1300
	1    0    0    -1  
$EndComp
Wire Wire Line
	6500 1300 7350 1300
Wire Wire Line
	7600 1300 7600 1600
Wire Wire Line
	5900 1300 4950 1300
$Comp
L main-rescue:PWR_FLAG-power-main-rescue #FLG0104
U 1 1 5BD2178B
P 7350 1300
F 0 "#FLG0104" H 7350 1375 50  0001 C CNN
F 1 "PWR_FLAG" H 7350 1474 50  0000 C CNN
F 2 "" H 7350 1300 50  0001 C CNN
F 3 "~" H 7350 1300 50  0001 C CNN
	1    7350 1300
	1    0    0    -1  
$EndComp
Connection ~ 7350 1300
Wire Wire Line
	7350 1300 7600 1300
Text Label 6900 1300 0    50   ~ 0
5VS_2
Wire Wire Line
	8200 5450 8000 5650
Wire Wire Line
	8000 5650 7000 5650
Wire Wire Line
	5950 5450 6900 5450
Wire Wire Line
	8000 5450 8200 5650
Wire Wire Line
	8200 5650 9350 5650
Wire Wire Line
	8200 5450 9350 5450
Wire Wire Line
	9200 5050 9350 5050
Wire Wire Line
	9100 5150 9350 5150
Wire Wire Line
	9000 5250 9350 5250
Wire Wire Line
	8200 2900 9200 2900
Wire Wire Line
	9200 2900 9200 5050
Wire Wire Line
	8200 2800 9100 2800
Wire Wire Line
	9100 2800 9100 5150
Wire Wire Line
	8200 2700 9000 2700
Wire Wire Line
	9000 2700 9000 5250
Wire Wire Line
	8200 2600 8900 2600
Wire Wire Line
	8900 2600 8900 5350
Wire Wire Line
	8900 5350 9350 5350
Wire Wire Line
	8200 2500 8800 2500
Wire Wire Line
	8800 2500 8800 5750
Wire Wire Line
	8800 5750 9350 5750
Wire Wire Line
	8200 2400 8700 2400
Wire Wire Line
	8700 2400 8700 5850
Wire Wire Line
	8700 5850 9350 5850
Wire Wire Line
	8200 2300 8600 2300
Wire Wire Line
	8600 2300 8600 5950
Wire Wire Line
	8600 5950 9350 5950
Wire Wire Line
	8200 2200 8500 2200
Wire Wire Line
	8500 2200 8500 6050
Wire Wire Line
	8500 6050 9350 6050
Wire Wire Line
	7600 3800 7600 4950
Connection ~ 7600 4950
Wire Wire Line
	7600 4950 9350 4950
Wire Wire Line
	7600 4950 7600 6150
NoConn ~ 7200 3300
NoConn ~ 8200 2000
NoConn ~ 8200 2100
Wire Wire Line
	7200 3000 6900 3000
Wire Wire Line
	6900 3000 6900 5450
Connection ~ 6900 5450
Wire Wire Line
	6900 5450 8000 5450
Wire Wire Line
	7200 3100 7000 3100
Wire Wire Line
	7000 3100 7000 5650
Connection ~ 7000 5650
Wire Wire Line
	7000 5650 5950 5650
NoConn ~ 7200 3200
Wire Wire Line
	4300 1400 4300 2100
Wire Wire Line
	4400 1300 4400 2000
Wire Wire Line
	1350 5100 2300 5100
$Comp
L main-rescue:Conn_01x02_Male-Connector-main-rescue J9
U 1 1 5BD40086
P 1150 5900
F 0 "J9" H 1256 6078 50  0000 C CNN
F 1 "5VS" H 1256 5987 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x02_Pitch2.54mm" H 1150 5900 50  0001 C CNN
F 3 "~" H 1150 5900 50  0001 C CNN
	1    1150 5900
	1    0    0    -1  
$EndComp
Wire Wire Line
	1350 5900 1550 5900
Connection ~ 1550 5900
Wire Wire Line
	1550 5900 1550 6250
Wire Wire Line
	1350 6000 1650 6000
Wire Wire Line
	1650 1200 1650 1800
Wire Wire Line
	1350 5500 1550 5500
Connection ~ 1550 5500
Wire Wire Line
	1550 5500 1550 5900
Wire Wire Line
	1350 5600 1650 5600
Connection ~ 1650 5600
Wire Wire Line
	1650 5600 1650 6000
Wire Wire Line
	1350 3500 1550 3500
Connection ~ 1550 3500
Wire Wire Line
	1350 3700 1750 3700
Wire Wire Line
	1350 3050 1550 3050
Connection ~ 1550 3050
Wire Wire Line
	1550 3050 1550 3500
Wire Wire Line
	1350 2750 2000 2750
Wire Wire Line
	1350 2550 1550 2550
Wire Wire Line
	1550 2550 1550 3050
Text Label 2600 2200 0    50   ~ 0
D2_2
Wire Wire Line
	1550 3500 1550 3950
Wire Wire Line
	1350 3950 1550 3950
Connection ~ 1550 3950
Wire Wire Line
	1550 3950 1550 4500
Wire Wire Line
	1750 900  1750 3250
Wire Wire Line
	2100 2500 2800 2500
Wire Wire Line
	2200 2600 2800 2600
$Comp
L spade_terminal:Spade_Terminal T1
U 1 1 5BE122D0
P 1150 900
F 0 "T1" H 1150 1000 50  0000 C CNN
F 1 "5V" H 1150 800 50  0000 C CNN
F 2 "spade_terminal:Spade_Terminal_1_4" H 1150 900 50  0001 C CNN
F 3 "" H 1150 900 50  0001 C CNN
	1    1150 900 
	1    0    0    -1  
$EndComp
$Comp
L spade_terminal:Spade_Terminal T3
U 1 1 5BE13A21
P 1150 5100
F 0 "T3" H 1150 5200 50  0000 C CNN
F 1 "24VS" H 1150 5000 50  0000 C CNN
F 2 "spade_terminal:Spade_Terminal_1_4" H 1150 5100 50  0001 C CNN
F 3 "" H 1150 5100 50  0001 C CNN
	1    1150 5100
	1    0    0    -1  
$EndComp
$Comp
L spade_terminal:Spade_Terminal T4
U 1 1 5BE141DB
P 1150 7000
F 0 "T4" H 1150 7100 50  0000 C CNN
F 1 "GND" H 1150 6900 50  0000 C CNN
F 2 "spade_terminal:Spade_Terminal_1_4" H 1150 7000 50  0001 C CNN
F 3 "" H 1150 7000 50  0001 C CNN
	1    1150 7000
	1    0    0    -1  
$EndComp
Wire Wire Line
	4600 2000 4400 2000
Wire Wire Line
	4600 2100 4300 2100
Wire Wire Line
	5400 2000 7200 2000
Wire Wire Line
	5400 2100 7200 2100
NoConn ~ 4600 2200
NoConn ~ 4600 2300
NoConn ~ 5400 2200
NoConn ~ 5400 2300
$Comp
L main-rescue:Conn_01x02_Male-Connector-main-rescue J10
U 1 1 5BD7937E
P 1150 6250
F 0 "J10" H 1256 6428 50  0000 C CNN
F 1 "5VS" H 1256 6337 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x02_Pitch2.54mm" H 1150 6250 50  0001 C CNN
F 3 "~" H 1150 6250 50  0001 C CNN
	1    1150 6250
	1    0    0    -1  
$EndComp
Wire Wire Line
	1350 6250 1550 6250
Connection ~ 1550 6250
Wire Wire Line
	1550 6250 1550 6600
Wire Wire Line
	1350 6350 1650 6350
Wire Wire Line
	1650 6350 1650 6000
Connection ~ 1650 6000
$Comp
L main-rescue:Conn_01x03_Male-Connector-main-rescue J2
U 1 1 5BD94D86
P 1150 2200
F 0 "J2" H 1256 2478 50  0000 C CNN
F 1 "Sensor0" H 1256 2387 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x03_Pitch2.54mm" H 1150 2200 50  0001 C CNN
F 3 "~" H 1150 2200 50  0001 C CNN
	1    1150 2200
	1    0    0    -1  
$EndComp
Wire Wire Line
	1550 2550 1550 2100
Wire Wire Line
	1550 2100 1350 2100
Connection ~ 1550 2550
Wire Wire Line
	1550 2100 1550 1600
Wire Wire Line
	1550 1600 1350 1600
Connection ~ 1550 2100
Wire Wire Line
	1350 1800 1650 1800
Connection ~ 1650 2650
Wire Wire Line
	4950 1200 4950 1300
Connection ~ 4950 1300
Wire Wire Line
	4950 1300 4950 1700
$Comp
L spade_terminal:Spade_Terminal T2
U 1 1 5BE139A1
P 1150 1200
F 0 "T2" H 1150 1300 50  0000 C CNN
F 1 "5VS" H 1150 1100 50  0000 C CNN
F 2 "spade_terminal:Spade_Terminal_1_4" H 1150 1200 50  0001 C CNN
F 3 "" H 1150 1200 50  0001 C CNN
	1    1150 1200
	1    0    0    -1  
$EndComp
Connection ~ 1650 1800
Wire Wire Line
	1650 2650 1650 5600
Connection ~ 1650 1200
Wire Wire Line
	1650 1200 2500 1200
Connection ~ 2500 1200
Wire Wire Line
	2500 1200 4950 1200
Wire Wire Line
	1650 1800 1650 2200
Wire Wire Line
	1350 2200 1650 2200
Connection ~ 1650 2200
Wire Wire Line
	1650 2200 1650 2650
Wire Wire Line
	2350 2200 2350 2050
Wire Wire Line
	2350 2200 2800 2200
Wire Wire Line
	2350 1750 2350 1700
Wire Wire Line
	2350 1700 1350 1700
Wire Wire Line
	1350 2300 2800 2300
Wire Wire Line
	2000 2400 2000 2750
Wire Wire Line
	2000 2400 2800 2400
Wire Wire Line
	1350 3150 2100 3150
Wire Wire Line
	2100 3150 2100 2500
Wire Wire Line
	1350 3600 2200 3600
Wire Wire Line
	2200 3600 2200 2600
Wire Wire Line
	2300 4050 2300 2700
Wire Wire Line
	2300 2700 2800 2700
Wire Wire Line
	1350 4050 2300 4050
Wire Wire Line
	1350 3250 1750 3250
Connection ~ 1750 3250
Wire Wire Line
	1750 3250 1750 3700
Text Label 2450 2700 2    50   ~ 0
D7
Wire Wire Line
	3200 1500 4200 1500
Wire Wire Line
	4200 1500 4200 2850
Connection ~ 3200 1500
Wire Wire Line
	3200 1500 3200 1600
Wire Wire Line
	4200 3150 4200 7000
Connection ~ 4200 7000
Wire Wire Line
	4200 7000 3200 7000
Wire Wire Line
	1550 7000 2850 7000
$Comp
L main-rescue:Conn_01x03_Male-Connector-main-rescue J6
U 1 1 5BF25C51
P 1150 4050
F 0 "J6" H 1256 4328 50  0000 C CNN
F 1 "Relay2" H 1256 4237 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x03_Pitch2.54mm" H 1150 4050 50  0001 C CNN
F 3 "~" H 1150 4050 50  0001 C CNN
	1    1150 4050
	1    0    0    -1  
$EndComp
Wire Wire Line
	1350 4150 1750 4150
Wire Wire Line
	1750 4150 1750 3700
Connection ~ 1750 3700
Wire Wire Line
	1350 4500 1550 4500
Connection ~ 1550 4500
Wire Wire Line
	1550 4500 1550 5500
Wire Wire Line
	1350 4600 2400 4600
Wire Wire Line
	2400 4600 2400 2800
Wire Wire Line
	2400 2800 2800 2800
Text Label 2550 2800 2    50   ~ 0
D8
$Comp
L main-rescue:Conn_01x02_Male-Connector-main-rescue J11
U 1 1 5BF738A8
P 1150 6600
F 0 "J11" H 1256 6778 50  0000 C CNN
F 1 "5VS" H 1256 6687 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x02_Pitch2.54mm" H 1150 6600 50  0001 C CNN
F 3 "~" H 1150 6600 50  0001 C CNN
	1    1150 6600
	1    0    0    -1  
$EndComp
Wire Wire Line
	1350 6600 1550 6600
Connection ~ 1550 6600
Wire Wire Line
	1550 6600 1550 7000
Wire Wire Line
	1350 6700 1650 6700
Wire Wire Line
	1650 6700 1650 6350
Connection ~ 1650 6350
$Comp
L main-rescue:Conn_01x02_Male-Connector-main-rescue J12
U 1 1 5BFFDCD1
P 2150 5500
F 0 "J12" H 2256 5678 50  0000 C CNN
F 1 "5V" H 2256 5587 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x02_Pitch2.54mm" H 2150 5500 50  0001 C CNN
F 3 "~" H 2150 5500 50  0001 C CNN
	1    2150 5500
	-1   0    0    -1  
$EndComp
$Comp
L main-rescue:Conn_01x02_Male-Connector-main-rescue J13
U 1 1 5C043D16
P 2150 5900
F 0 "J13" H 2256 6078 50  0000 C CNN
F 1 "5V" H 2256 5987 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x02_Pitch2.54mm" H 2150 5900 50  0001 C CNN
F 3 "~" H 2150 5900 50  0001 C CNN
	1    2150 5900
	-1   0    0    -1  
$EndComp
$Comp
L main-rescue:Conn_01x02_Male-Connector-main-rescue J14
U 1 1 5C043D64
P 2150 6250
F 0 "J14" H 2256 6428 50  0000 C CNN
F 1 "5V" H 2256 6337 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x02_Pitch2.54mm" H 2150 6250 50  0001 C CNN
F 3 "~" H 2150 6250 50  0001 C CNN
	1    2150 6250
	-1   0    0    -1  
$EndComp
Wire Wire Line
	1950 5500 1550 5500
Wire Wire Line
	1950 5900 1550 5900
Wire Wire Line
	1950 6250 1550 6250
Wire Wire Line
	1750 4150 1750 5600
Wire Wire Line
	1750 5600 1950 5600
Connection ~ 1750 4150
Wire Wire Line
	1750 5600 1750 6000
Wire Wire Line
	1750 6000 1950 6000
Connection ~ 1750 5600
Wire Wire Line
	1750 6000 1750 6350
Wire Wire Line
	1750 6350 1950 6350
Connection ~ 1750 6000
$Comp
L main-rescue:Conn_01x02_Male-Connector-main-rescue J15
U 1 1 5C0A867B
P 2650 6600
F 0 "J15" H 2756 6778 50  0000 C CNN
F 1 "24S" H 2756 6687 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x02_Pitch2.54mm" H 2650 6600 50  0001 C CNN
F 3 "~" H 2650 6600 50  0001 C CNN
	1    2650 6600
	-1   0    0    -1  
$EndComp
Wire Wire Line
	2450 6600 1550 6600
Wire Wire Line
	2450 6700 2300 6700
Wire Wire Line
	2300 6700 2300 5100
Connection ~ 2300 5100
Wire Wire Line
	2300 5100 5500 5100
$Comp
L main-rescue:Conn_01x02_Male-Connector-main-rescue J16
U 1 1 5C0D0641
P 2550 5500
F 0 "J16" H 2656 5678 50  0000 C CNN
F 1 "3.3V" H 2656 5587 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x02_Pitch2.54mm" H 2550 5500 50  0001 C CNN
F 3 "~" H 2550 5500 50  0001 C CNN
	1    2550 5500
	1    0    0    -1  
$EndComp
Wire Wire Line
	3350 3950 6000 3950
Connection ~ 6000 3950
Wire Wire Line
	3200 3800 3200 5500
Wire Wire Line
	2750 5500 3200 5500
Connection ~ 3200 5500
Wire Wire Line
	3200 5500 3200 7000
Wire Wire Line
	2750 5600 3350 5600
Wire Wire Line
	3350 3950 3350 5600
$EndSCHEMATC
