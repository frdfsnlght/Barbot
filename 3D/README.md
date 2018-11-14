# 3D

These are SketchUp Make 2017 files for the most part.

## Enclosure

This file contains the model for the entire enclosure and most of the internal parts, except for the
pumps. Printable parts have been exported as STL to the STLs directory.

## Pump

This file contains all the parts for the planetary gear, peristaltic pump I designed. Every part except
the stepper motor can be printed and all parts have been exported to the STLs directory.

## Print Settings

All these parts were sliced with Slic3r Prusa Edition for an Original Prusa MK3 with a layer height of 0.15mm.

File            | Part                                                      | Material  | Infill            | Perimeters| Top/Bot   | Quantity
---             | ---                                                       | ---       | ---               | ---       | ---       | ---
Enclosure       | [Dispenser Head Part A](./3D/STLs/Dispenser Head Part A.stl)   | PLA       | 40% Grid          | 2         | 7/5       | 1
Enclosure       | [Dispenser Head Part B](STLs/Dispenser Head Part B.stl)   | PLA       | 20% Grid          | 2         | 7/5       | 1
Enclosure       | [Dispenser Head Part C](STLs/Dispenser Head Part C.stl)   | PLA       | 40% Grid          | 2         | 7/5       | 1
Enclosure       | [Dispenser Head Part D](STLs/Dispenser Head Part D.stl)   | PETG      | 40% Grid          | 2         | 7/5       | 1
Enclosure       | [Touch Screen Bracket](STLs/Touchscreen Bracket.stl)      | PETG      | 50% Grid          | 2         | 7/5       | 2     0.75
Enclosure       | [Speaker Grill](STLs/Speaker Grill.stl)                   | PETG      | 20% Honeycomb     | 8         | 0/0       | 2     1.5
Enclosure       | [Drip Tray](STLs/Drip Tray.stl)                           | PETG      | 20% Grid          | 2         | 7/5       | 1     8.25
Pump            | [Sun Gear](STLs/Sun Gear.stl)                             | PLA       | 100% Rectilinear  | 5         | 7/5       | 32    X
Pump            | [Sun Roller](STLs/Sun Roller.stl)                         | PLA       | 50% Grid          | 5         | 7/5       | 16    X
Pump            | [Planet Gear](STLs/Planet Gear.stl)                       | PLA       | 100% Rectilinear  | 5         | 7/5       | 64        5.5 (16)/7.75 (22)
Pump            | [Planet Roller](STLs/Planet Roller.stl)                   | PLA       | 50% Grid          | 5         | 7/5       | 32    X
Pump            | [Clamp Block Left](STLs/Clamp Block Left.stl)             | PLA       | 20% Grid          | 2         | 7/5       | 16    X
Pump            | [Clamp Block Right](STLs/Clamp Block Right.stl)           | PLA       | 20% Grid          | 2         | 7/5       | 16    X
Pump            | [Motor Plate](STLs/Motor Plate.stl)                       | PLA       | 20% Grid          | 2         | 7/5       | 16    X
Pump            | [Ring Plate A](STLs/Ring Plate A.stl)                     | PLA       | 50% Grid          | 5         | 7/5       | 16    X
Pump            | [Ring Plate B](STLs/Ring Plate B.stl)                     | PLA       | 50% Grid          | 5         | 7/5       | 16    X
Pump            | [Body Plate A](STLs/Body Plate A.stl)                     | PLA       | 50% Grid          | 5         | 7/5       | 16    X
Pump            | [Body Plate B](STLs/Body Plate B.stl)                     | PLA       | 50% Grid          | 5         | 7/5       | 16    X

## Bill of Materials

This is a mostly complete list of every conceivable off-the-shelf part that will be required. You can find everything online,
but some of it can be found at a local, well stocked hardware store.
I've included links and approximate pricing where I could. Some of the online quantities are way more than you'll need.

### Hardware

Each item is linked to a McMaster-Carr product page and lists a price as of November 2018. I actually purchased much of this
from my local hardware store, but the larger quantity items were bought online.

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
 *Hinge Supports*                                                                           |   4
[#8 x 1<sup>1</sup>/<sub>4</sub>" SS Phillips Oval Head Machine Screws](https://www.mcmaster.com/91802A201)       | 100 | $8.95
 *Fan*                                                                                      |   4
[#8-32 SS Hex Nuts](https://www.mcmaster.com/91841A009)                                     | 100 | $3.65
 *Fan*                                                                                      |   4
[#6 x <sup>5</sup>/<sub>8</sub>" SS Phillips Flat Head Metal Screws](https://www.mcmaster.com/90065A149)          | 100 | $3.89
 *Controller*                                                                               |   1
 *Hinges*                                                                                   |   4
[#6 x <sup>3</sup>/<sub>8</sub>" SS Phillips Flat Head Machine Screws](https://www.mcmaster.com/91771A146)        | 100 | $5.13
 *Hinges*                                                                                   |   4
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
[3mm x 30mm SS Socket Head Machine Screws](https://www.mcmaster.com/91292A022)              |  50 | $4.08
 *Dispenser Head*                                                                           |   4
[3mm x 25mm SS Socket Head Machine Screws](https://www.mcmaster.com/91292A020)              | 100 | $6.87
 *Pumps*                                                                                    |  80
[3mm x 20mm SS Socket Head Machine Screws](https://www.mcmaster.com/91292A123)              | 100 | $6.44
 *Dispenser Head*                                                                           |   1
 *Speakers*                                                                                 |   8
[3mm x 10mm SS Hex Drive Flat Head Machine Screws](https://www.mcmaster.com/92125A130)      | 100 | $5.81
 *Power Socket*                                                                             |   2
[3mm x 8mm SS Phillips Pan Head Machine Screws](https://www.mcmaster.com/92000A118)         | 100 | $4.33
 *Touchscreen Bracket*                                                                      |   4
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

### Electronics

Here's a list of all the electrical parts you'll need. Note, you'll also need the circuit boards that also part of this project,
as well as wire, a soldering iron, connectors, etc.

* Raspberry Pi 3 Model B (Amazon)
* 16GB Micro SD Card (Amazon)
* Teensy 3.2 (OSHPark with PCB order)
* Arduino Pro Mini
* Relays (eBay)
* Amplifier (Amazon)
* Speakers (Salvage)
* Stepper Drivers (AliExpress)
* 10 uF Capacitors (AliExpress)
* 1000 uF Capacitor (Amazon)
* Spade Solder Terminals (Amazon)
* Power Socket (eBay)
* Switch (Amazon)
* Stepper Motors (AliExpress)
* 80mm Fan (Salvage)
* IR Sensor (Amazon)
* 5V 12A Power Supply (Amazon)
* 24V 5A Power Supply (eBay)
* LEDs (eBay)
* Power Cord (Surplus)

### Other

Here's a few other important parts that didn't fit well in any other category.

* Funnel (Amazon)
* Hinges (Amazon)
* <sup>1</sup>/<sub>8</sub>" x 2' x 4' Acrylic Sheet, Black (Amazon)
* 4' x 4' x <sup>3</sup>/<sub>4</sub>" Birch Plywood (Surplus)
* Solid Birch Plank (Surplus)
* <sup>3</sup>/<sub>16</sub>" Brake Line (Amazon)
* 8mm/6mm Silicone Tubing (Amazon)
* 6mm/4mm Silicone Tubing (Amazon)

