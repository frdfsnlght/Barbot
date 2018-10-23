EESchema Schematic File Version 4
LIBS:pump-cache
EELAYER 26 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 9 9
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L stepper_driver:DRV8825_Carrier A1
U 1 1 5BCF6E5D
P 5700 3700
AR Path="/5BCF8DAA/5BCF6E5D" Ref="A1"  Part="1" 
AR Path="/5BCF8E71/5BCF6E5D" Ref="A2"  Part="1" 
AR Path="/5BCF8E75/5BCF6E5D" Ref="A3"  Part="1" 
AR Path="/5BCF8E79/5BCF6E5D" Ref="A4"  Part="1" 
AR Path="/5BCF8E7D/5BCF6E5D" Ref="A5"  Part="1" 
AR Path="/5BCF8E81/5BCF6E5D" Ref="A6"  Part="1" 
AR Path="/5BCF8E85/5BCF6E5D" Ref="A7"  Part="1" 
F 0 "A7" H 5350 4450 50  0000 C CNN
F 1 "DRV8825_Carrier" H 6150 4450 50  0000 C CNN
F 2 "Module:DRV8825_Carrier" H 5850 2950 50  0001 L CNN
F 3 "https://www.pololu.com/product/2133" H 5500 4550 50  0001 C CNN
	1    5700 3700
	1    0    0    -1  
$EndComp
$Comp
L Device:CP1 C1
U 1 1 5BCF6EE0
P 4600 4500
AR Path="/5BCF8DAA/5BCF6EE0" Ref="C1"  Part="1" 
AR Path="/5BCF8E71/5BCF6EE0" Ref="C2"  Part="1" 
AR Path="/5BCF8E75/5BCF6EE0" Ref="C3"  Part="1" 
AR Path="/5BCF8E79/5BCF6EE0" Ref="C4"  Part="1" 
AR Path="/5BCF8E7D/5BCF6EE0" Ref="C5"  Part="1" 
AR Path="/5BCF8E81/5BCF6EE0" Ref="C6"  Part="1" 
AR Path="/5BCF8E85/5BCF6EE0" Ref="C7"  Part="1" 
F 0 "C7" V 4715 4546 50  0000 L CNN
F 1 "100u" H 4715 4455 50  0000 L CNN
F 2 "" H 4600 4500 50  0001 C CNN
F 3 "~" H 4600 4500 50  0001 C CNN
	1    4600 4500
	1    0    0    -1  
$EndComp
$Comp
L Connector:Conn_01x04_Male J1
U 1 1 5BCF6FDD
P 6700 3400
AR Path="/5BCF8DAA/5BCF6FDD" Ref="J1"  Part="1" 
AR Path="/5BCF8E71/5BCF6FDD" Ref="J2"  Part="1" 
AR Path="/5BCF8E75/5BCF6FDD" Ref="J3"  Part="1" 
AR Path="/5BCF8E79/5BCF6FDD" Ref="J4"  Part="1" 
AR Path="/5BCF8E7D/5BCF6FDD" Ref="J5"  Part="1" 
AR Path="/5BCF8E81/5BCF6FDD" Ref="J6"  Part="1" 
AR Path="/5BCF8E85/5BCF6FDD" Ref="J7"  Part="1" 
F 0 "J7" H 6672 3373 50  0000 R CNN
F 1 "Motor" H 6672 3282 50  0000 R CNN
F 2 "" H 6700 3400 50  0001 C CNN
F 3 "~" H 6700 3400 50  0001 C CNN
	1    6700 3400
	-1   0    0    -1  
$EndComp
Text HLabel 3700 3300 0    50   Input ~ 0
~ENABLE
Text HLabel 3700 4100 0    50   Input ~ 0
STEP
Text HLabel 3700 4200 0    50   Input ~ 0
DIR
Text HLabel 3700 2650 0    50   Input ~ 0
24V
Text HLabel 3700 4750 0    50   Input ~ 0
GND
Wire Wire Line
	3700 3300 5200 3300
NoConn ~ 5200 3400
NoConn ~ 5200 3500
Wire Wire Line
	3700 2650 4600 2650
Wire Wire Line
	5700 2650 5700 2900
Wire Wire Line
	3700 4750 4600 4750
Wire Wire Line
	5600 4750 5600 4500
Wire Wire Line
	5600 4750 5800 4750
Wire Wire Line
	5800 4750 5800 4500
Connection ~ 5600 4750
Wire Wire Line
	4600 4650 4600 4750
Connection ~ 4600 4750
Wire Wire Line
	4600 4750 5600 4750
Wire Wire Line
	4600 4350 4600 2650
Connection ~ 4600 2650
Wire Wire Line
	4600 2650 5700 2650
Wire Wire Line
	3700 4200 5200 4200
Wire Wire Line
	3700 4100 5200 4100
Wire Wire Line
	5200 3700 5100 3700
Wire Wire Line
	5100 3700 5100 3800
Wire Wire Line
	5100 3800 5200 3800
NoConn ~ 5200 3900
NoConn ~ 6200 3800
Text HLabel 3700 3700 0    50   Input ~ 0
5V
Wire Wire Line
	3700 3700 5100 3700
Connection ~ 5100 3700
Wire Wire Line
	6200 3300 6500 3300
Wire Wire Line
	6200 3400 6500 3400
Wire Wire Line
	6200 3500 6500 3500
Wire Wire Line
	6200 3600 6500 3600
$EndSCHEMATC
