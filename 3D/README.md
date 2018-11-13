# 3D

These are SketchUp Pro 2017 files for the most part.

## Enclosure

This file contains the model for the entire enclosure and most of the internal parts, except for the
pumps. Printable parts have been exported as STL to the STLs directory.

## Pump

This file contains all the parts for the planetary gear, peristaltic pump I designed. Every part except
the stepper motor can be printed and all parts have been exported to the STLs directory.

## Print Settings

File            | Part                        | Material  | Layer Height| Infill            | Perimeters| Top/Bot   | Quantity
---             | ---                         | ---       | ---         | ---               | ---       | ---       | ---
Enclosure       | Dispenser Head Part A       | PLA       | 0.15        | 40% Grid          | 2         | 7/5       | 1
Enclosure       | Dispenser Head Part B       | PLA       | 0.15        | 20% Grid          | 2         | 7/5       | 1
Enclosure       | Dispenser Head Part C       | PLA       | 0.15        | 40% Grid          | 2         | 7/5       | 1
Enclosure       | Dispenser Head Part D       | ABS       | 0.15        | 40% Grid          | 2         | 7/5       | 1
Enclosure       | Touch Screen Bracket        | PETG      | 0.15        |
Enclosure       | Speaker Grill               | PETG      | 0.15        |
Enclosure       | Drip Tray                   | PETG      | 0.15        |
Pump            | Sun Gear                    | PLA       | 0.15        | 100% Rectilinear  | 5         | 7/5       | 32    X
Pump            | Sun Roller                  | PLA       | 0.15        | 50% Grid          | 5         | 7/5       | 16    X
Pump            | Planet Gear                 | PLA       | 0.15        | 100% Rectilinear  | 5         | 7/5       | 64        5.5 (16)/7.75 (22)
Pump            | Planet Roller               | PLA       | 0.15        | 50% Grid          | 5         | 7/5       | 32    X
Pump            | Clamp Block Left            | PLA       | 0.15        | 20% Grid          | 2         | 7/5       | 16    X
Pump            | Clamp Block Right           | PLA       | 0.15        | 20% Grid          | 2         | 7/5       | 16    X
Pump            | Motor Plate                 | PLA       | 0.15        | 20% Grid          | 2         | 7/5       | 16    X
Pump            | Ring Plate A                | PLA       | 0.15        | 50% Grid          | 5         | 7/5       | 16    X
Pump            | Ring Plate B                | PLA       | 0.15        | 50% Grid          | 5         | 7/5       | 16    4    7 (4)
Pump            | Body Plate A                | PLA       | 0.15        | 50% Grid          | 5         | 7/5       | 16    X
Pump            | Body Plate B                | PLA       | 0.15        | 50% Grid          | 5         | 7/5       | 16    X

## Bill of Materials

### Hardware

This is a mostly complete list of nuts/bolts/hardware that will be required. Each item is linked to a McMaster-Carr
product page and lists a unit price as November 2018.

Description                                                                                 | Quantity | Price
---                                                                                         | ---      | ---
[#8 x <sup>5</sup>/<sub>8</sub>" SS Phillips Oval Head Metal Screws](https://www.mcmaster.com/90315A467)          | 100 | $6.03
 *Side Panels*                                                                              |  16
 *Dispenser Panels*                                                                         |  16
 *Back*                                                                                     |   6
 *Controller*                                                                               |  14
 *Top Panel Brackets*                                                                       |   8
 *Pump Holder Brackets*                                                                     |   8
 *PCB Panel Brackets*                                                                       |   4
 *Power Supply Panel*                                                                       |   2
 *Relay Panel*                                                                              |   2
[#8 x 1" SS Phillips Round Head Metal Screws](https://www.mcmaster.com/92470A199)           | 100 | $8.13
 *LED Panel*                                                                                |   2
[#8 x <sup>5</sup>/<sub>8</sub>" SS Phillips Flat Head Metal Screws](https://www.mcmaster.com/90065A195)          | 100 | $5.50
 *Dispenser Panels*                                                                         |   2
 *Front*                                                                                    |   2
 *Pumps*                                                                                    |  32
[#8 x 1<sup>1</sup>/<sub>4</sub>" SS Phillips Oval Head Machine Screws](https://www.mcmaster.com/91802A201)       | 100 | $8.95
 *Fan*                                                                                      |   4
[#8-32 SS Hex Nuts](https://www.mcmaster.com/91841A009)                                     | 100 | $3.65
 *Fan*                                                                                      |   4
[#6 x 5/8" SS Phillips Flat Head Metal Screws](https://www.mcmaster.com/90065A149)          | 100 | $3.89
 *Controller*                                                                               |   1
 *Controller Hinges*                                                                        |   4
[#4-40 x 5/8" Steel Phillips Flat Head Machine Screws](https://www.mcmaster.com/90273A112)  | 100 | $2.74
 *PCB Panel*                                                                                |  14
 *Replay Panel*                                                                             |   8
 *Amplifier*                                                                                |   4
[#4-40 Steel Hex Nuts](https://www.mcmaster.com/90480A005)                                  | 100 | $0.89
 *PCB Panel*                                                                                |  14
 *Replay Panel*                                                                             |   8
 *Amplifier*                                                                                |   4
[#8 x 1/4" x 1/4" Nylon Spacers](https://www.mcmaster.com/94639A293)                        | 100 | $8.75
 *PCBs*                                                                                     |  14
 *Relays*                                                                                   |   8
 *LED Panel*                                                                                |   4
 *Amplifier*                                                                                |   4
 *Speakers*                                                                                 |   8
[3mm x 30mm SS Socket Head Machine Screws](https://www.mcmaster.com/91292A022)              |  50 | $4.08
 *Dispenser Head*                                                                           |   4
[3mm x 25mm SS Socket Head Machine Screws](https://www.mcmaster.com/91292A020)              | 100 | $6.87
 *Pumps*                                                                                    |  80
[3mm x 20mm SS Socket Head Machine Screws](https://www.mcmaster.com/91292A123)              | 100 | $6.44
 *Dispenser Head*                                                                           |   1
[3mm x 10mm SS Hex Drive Flat Head Machine Screws](https://www.mcmaster.com/92125A130)      | 100 | $5.81
 *Power Socket*                                                                             |   2
[3mm x 8mm SS Hex Drive Flat Head Machine Screws](https://www.mcmaster.com/92125A128)       | 100 | $3.54
 *Power Supply Panel*                                                                       |   6
 *Pumps*                                                                                    |  64
[3mm SS Hex Nuts](https://www.mcmaster.com/91828A211)                                       | 100 | $5.55
 *Power Socket*                                                                             |   2
 *Pumps*                                                                                    |  80
 *Dispenser Head*                                                                           |   5
 *Speakers*                                                                                 |   8
[3mm SS Slim Hex Nuts](https://www.mcmaster.com/90710A030)                                  | 100 | $6.86
 *Pumps*                                                                                    |  32
[3mm x 8mm SS Flat Tip Set Screws](https://www.mcmaster.com/92605A102)                      |  25 | $2.97
 *Pumps*                                                                                    |  32
[3mm x 8mm SS Phillips Pan Head Machine Screws](https://www.mcmaster.com/92000A118)         | 100 | $4.33
 *PCB Panel*                                                                                |   4
[<sup>1</sup>/<sub>8</sub>" x 1 <sup>3</sup>/<sub>8</sub>" OD O-Ring](https://www.mcmaster.com/9452K36)     | 100 | $8.81
 *Dispenser Head*                                                                           |   1
[3/4" x 9/16" Rubber Feet](https://www.mcmaster.com/8884T21)                                |  10 | $5.17
 *Bottom*                                                                                   |   4

Touchscreen bracket:
3mm x ?                                     4

Speakers:
M3 x ? SS Socket Head Machine Screws        8
x M3 SS Hex Nuts                              8

### Electronics

* Raspberry Pi 3 Model B
* Teensy 3.2
* Arduino Pro Mini
* Relays (eBay)
* Amplifier (Amazon)
* Speakers
* Stepper Drivers
* 10 uF Capacitors
* 1000 uF Capacitor (Amazon)
* Spade Solder Terminals (Amazon)
* Power Socket (eBay)
* Switch
* Stepper Motors
* 80mm Fan
* IR Sensor (Amazon)
* 5V 12A Power Supply (Amazon)
* 24V 5A Power Supply (eBay)
* LEDs (eBay)

### Other
* Funnel (Amazon)
* Hinges (Amazon)
