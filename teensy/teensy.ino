/*
Copyright 2018 Thomas A. Bennedum

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
*/

/*
    https://github.com/luni64/TeensyStep
    NOTE: You must set the MaxMotors constant to 17 (PUMPS + 1), line 8 in StepControl.h!
*/

#include <Arduino.h>
#include <avr_functions.h>
#include <StepControl.h>

constexpr int PIN_LED                   = LED_BUILTIN;
constexpr int PIN_ENABLE                = 11;
constexpr int PIN_DIR                   = 10;
constexpr int SERIAL1_PIN_RX            = 0;
constexpr int SERIAL1_PIN_TX            = 1;

constexpr int PUMPS                     = 16;

constexpr int PUMP_MAX_SPEED            = 500000;
constexpr int PUMP_MIN_SPEED            = 40;
constexpr int PUMP_DEF_SPEED            = 15000;
constexpr int PUMP_MAX_ACCEL            = 500000;
constexpr int PUMP_MIN_ACCEL            = 1;
constexpr int PUMP_DEF_ACCEL            = 7500;

constexpr int PUMP_CONTROLLERS          = 4;

constexpr int INPUT_BUFFERS             = 2;
constexpr int INPUT_BUFFER_LENGTH       = 32;
constexpr int BUF_SERIAL                = 0;
constexpr int BUF_SERIAL1               = 1;

constexpr unsigned long LED_TOGGLE_INTERVAL = 500;

constexpr int ERR_OK                    = 0;
constexpr int ERR_PUMPS_ARE_RUNNING     = 1;

constexpr int SERIAL_SPEEDS[]           = {115200, 58824, 38400, 19200, 9600};
constexpr int NUM_SERIAL_SPEEDS         = sizeof(SERIAL_SPEEDS) / sizeof(int);
constexpr int PING_TIMEOUT              = 3000;

constexpr int CHECKSUM_RETRIES          = 3;


typedef struct {
    char data[INPUT_BUFFER_LENGTH + 1];
    uint16_t length;
} inputBuffer_t;
    
inputBuffer_t inputBuffers[INPUT_BUFFERS];
int ch;

Stepper pump0(23, PIN_DIR);
Stepper pump1(22, PIN_DIR);
Stepper pump2(21, PIN_DIR);
Stepper pump3(20, PIN_DIR);
Stepper pump4(19, PIN_DIR);
Stepper pump5(18, PIN_DIR);
Stepper pump6(17, PIN_DIR);
Stepper pump7(16, PIN_DIR);
Stepper pump8(9, PIN_DIR);
Stepper pump9(8, PIN_DIR);
Stepper pump10(7, PIN_DIR);
Stepper pump11(6, PIN_DIR);
Stepper pump12(5, PIN_DIR);
Stepper pump13(4, PIN_DIR);
Stepper pump14(3, PIN_DIR);
Stepper pump15(2, PIN_DIR);

Stepper* allPumps[] = {&pump0, &pump1, &pump2, &pump3, &pump4, &pump5, &pump6, &pump7,
                       &pump8, &pump9, &pump10, &pump11, &pump12, &pump13, &pump14, &pump15};

StepControl<> pumpCtrl0;
StepControl<> pumpCtrl1;
StepControl<> pumpCtrl2;
StepControl<> pumpCtrl3;
StepControl<>* allPumpControllers[] = {&pumpCtrl0, &pumpCtrl1, &pumpCtrl2, &pumpCtrl3};

StepControl<>* pumpControllers[PUMPS];
int pumpDir = 0;
int pumpSpeed = PUMP_DEF_SPEED;
unsigned pumpAccel = PUMP_DEF_ACCEL;
bool pumpsEnabled = false;
bool pumpsFlushing = false;

int serialSpeed = 0;

bool ledOn = false;
uint32_t lastLEDToggle = 0;

uint8_t checksumRetries = 0;
char lastSerial1Command[INPUT_BUFFER_LENGTH + 1];



void setup() {
    Serial.begin(115200); // speed is ignored
    
    detectSerial1Speed();
    
    pinMode(PIN_LED, OUTPUT);
    pinMode(PIN_ENABLE, OUTPUT);
    turnOffLED();
    disablePumps();
    
    sendMessage("Hello");
}

void loop() {
    loopSerial();
    loopSerial1();
    loopPumps();
    loopLED();
}

void loopSerial() {
    while (Serial.available()) {
        ch = Serial.read();
        if ((ch == '\r') || (ch == '\n')) {
            if (inputBuffers[BUF_SERIAL].length) {
                processCommand();
            }
            resetInputBuffer(BUF_SERIAL);
        } else if (ch == 8) {
            if (inputBuffers[BUF_SERIAL].length) {
                inputBuffers[BUF_SERIAL].length--;
            }
        } else if (ch == 27) {
            if (inputBuffers[BUF_SERIAL].length) {
                resetInputBuffer(BUF_SERIAL);
                send("CANCELED\n");
            }
        } else if ((ch >= 32) && (ch <= 126)) {
            if (inputBuffers[BUF_SERIAL].length == INPUT_BUFFER_LENGTH) {
                resetInputBuffer(BUF_SERIAL);
                sendError("overflow");
                return;
            }
            appendInputBuffer(BUF_SERIAL, ch);
        }
    }
}

void loopSerial1() {

    while (serialSpeed && Serial1.available()) {
        ch = Serial1.read();
        if ((ch == '\r') || (ch == '\n')) {
            if (inputBuffers[BUF_SERIAL1].length) {
                if ((strcmp(inputBuffers[BUF_SERIAL1].data, "!CHK") == 0) && (checksumRetries < CHECKSUM_RETRIES)) {
                    checksumRetries++;
                    sendMessage("retry");
                    Serial1.println(lastSerial1Command);
                } else {
                    send(inputBuffers[BUF_SERIAL1].data);
                    sendChar('\n');
                }
            }
            resetInputBuffer(BUF_SERIAL1);
        } else {
            appendInputBuffer(BUF_SERIAL1, ch);
        }
    }
}

void loopPumps() {
    bool running = false;
    for (byte i = 0; i < PUMPS; i++) {
        if (pumpControllers[i]) {
            if (! pumpControllers[i]->isRunning()) {
                pumpControllers[i] = NULL;
                sendPumpStopped(i);
            } else {
                running = true;
            }
        }
    }
    if (running) {
        delay(1);
    } else {
        if (pumpsFlushing)
            pumpsFlushing = false;
        if (pumpsEnabled) {
            disablePumps();
            pumpDir = 0;
        }
    }
}

void loopLED() {
    if (! pumpsEnabled && ((millis() - lastLEDToggle) >= LED_TOGGLE_INTERVAL)) {
        lastLEDToggle = millis();
        toggleLED();
    }
}

void detectSerial1Speed() {
    for (int i = 0; i < NUM_SERIAL_SPEEDS; i++) {
        send("# trying ");
        sendInt(SERIAL_SPEEDS[i]);
        sendChar('\n');
        
        Serial1.begin(SERIAL_SPEEDS[i], SERIAL_8N1);
        if (ping()) {
            serialSpeed = SERIAL_SPEEDS[i];
            send("# detected ");
            sendInt(serialSpeed);
            sendChar('\n');
            return;
        }
    }
    sendError("unable to detect serial speed");
    serialSpeed = 0;
}

bool ping() {
    Serial1.println("PING");
    unsigned long time = millis();
    while ((millis() - time) < PING_TIMEOUT) {
        while (Serial1.available()) {
            ch = Serial1.read();
            if ((ch == '\r') || (ch == '\n')) {
                if (inputBuffers[BUF_SERIAL1].length && 
                    strcmp(inputBuffers[BUF_SERIAL1].data, "PONG") == 0) {
                    resetInputBuffer(BUF_SERIAL1);
                    return true;
                }
                resetInputBuffer(BUF_SERIAL1);
            } else if (inputBuffers[BUF_SERIAL1].length == 0) {
                if (ch == 'P') {
                    appendInputBuffer(BUF_SERIAL1, ch);
                }
            } else if ((ch >= 32) && (ch <= 126)) {
                if (inputBuffers[BUF_SERIAL1].length == INPUT_BUFFER_LENGTH) {
                    resetInputBuffer(BUF_SERIAL1);
                } else {
                    appendInputBuffer(BUF_SERIAL1, ch);
                }
            }
        }
    }
    return false;
}

void resetInputBuffer(int buf) {
    inputBuffers[buf].data[0] = '\0';
    inputBuffers[buf].length = 0;
}

void appendInputBuffer(int buf, char ch) {
    inputBuffers[buf].data[inputBuffers[buf].length++] = ch;
    inputBuffers[buf].data[inputBuffers[buf].length] = '\0';
}

void enablePumps() {
    digitalWriteFast(PIN_ENABLE, LOW);
    turnOnLED();
    pumpsEnabled = true;
}

void disablePumps() {
    digitalWriteFast(PIN_ENABLE, HIGH);
    turnOffLED();
    pumpsEnabled = false;
}

void turnOnLED() {
    digitalWriteFast(PIN_LED, HIGH);
    ledOn = true;
}

void turnOffLED() {
    digitalWriteFast(PIN_LED, LOW);
    ledOn = false;
}

void toggleLED() {
    if (ledOn) turnOffLED();
    else turnOnLED();
}

void setPumpSpeed(int speed) {
    for (byte i = 0; i < PUMPS; i++) {
        allPumps[i]->setMaxSpeed(speed);
        allPumps[i]->setAcceleration(pumpAccel);
        pumpControllers[i] = NULL;
    }
}

void processCommand() {
    char* cmd = inputBuffers[BUF_SERIAL].data;
    int len = inputBuffers[BUF_SERIAL].length;
    
    switch (cmd[0]) {
        case 'C':
            if (! processChecksum(cmd, len)) break;
        case 'c':
            processCommCommand(cmd + 1);
            break;
        case 'P':
            if (! processChecksum(cmd, len)) break;
        case 'p':
            processPumpCommand(cmd + 1);
            break;
        default:
            if (serialSpeed) {
                strcpy(lastSerial1Command, inputBuffers[BUF_SERIAL].data);
                Serial1.println(lastSerial1Command);
                checksumRetries = 0;
            }
            break;
    }
}

bool processChecksum(char* cmd, int len) {
    if ((len <= 3) || (cmd[len - 3] != '~')) {
        sendError("CHK");
        return false;
    }
    char* hex = cmd + len - 2;
    uint8_t sentCS = readHex(&hex);
    uint8_t calcCS = 0;
    for (int i = 0; i < len; i++)
        calcCS ^= cmd[i];
    if (sentCS != calcCS) {
        sendError("CHK");
        return false;
    }
    cmd[len - 3] = 0;
    return true;
}

// =========== Comm commands
void processCommCommand(char* cmd) {
    switch (cmd[0]) {
        case 'D':
        case 'd':
            detectSerial1Speed();
            cmdCommStatus();
            sendOK();
            return;
        case 'P':
        case 'p':
            if (ping())
                sendOK();
            else
                sendError("timeout");
            break;
        case '?':
            cmdCommStatus();
            break;
        default:
            sendError("invalid comm command");
            break;
    }
}

void cmdCommStatus() {
    send("speed: ");
    sendInt(serialSpeed);
    sendChar('\n');
    
    sendOK();
}

// =========== Pump commands

void processPumpCommand(char* cmd) {
    switch (cmd[0]) {
        case 'P':
        case 'p':
            cmdPumpPump(cmd + 1);
            break;
        case 'H':
        case 'h':
            cmdPumpHalt(cmd + 1);
            break;
        case 'F':
        case 'f':
            cmdPumpFlush(cmd + 1);
            break;
        case 'S':
        case 's':
            cmdPumpSpeed(cmd + 1);
            break;
        case 'A':
        case 'a':
            cmdPumpAcceleration(cmd + 1);
            break;
        case '?':
            cmdPumpStatus();
            break;
        default:
            sendError("invalid pump command");
            break;
    }
}

/*
PP<#>,<[-]steps>,<speed>,<accel>
*/
void cmdPumpPump(char* str) {
    byte pumpNum;
    if (str[0] == '?') {
        // debugging stuff to allow ? as pump num to mean next unused pump
        pumpNum = PUMPS + 1;
        for (byte i = 0; i < PUMPS; i++) {
            if (! pumpControllers[i]) {
                pumpNum = i;
                break;
            }
        }
        str++;
    } else {
        pumpNum = readUInt(&str);
    }
    readDelim(&str);
    
    if (pumpNum >= PUMPS) {
        sendError("invalid pump");
        return;
    }
    if (pumpControllers[pumpNum]) {
        sendError("pump is running");
        return;
    }
    
    int steps = readInt(&str);
    readDelim(&str);
    if (steps == 0) {
        sendError("invalid steps");
        return;
    }
    int dir = steps < 0 ? -1 : 1;
    
    if ((pumpDir != 0) && (dir != pumpDir)) {
        sendError("invalid direction");
        return;
    }
    
    int speed = readUInt(&str);
    readDelim(&str);
    if (speed == 0) speed = pumpSpeed;
    
    int accel = readUInt(&str);
    readDelim(&str);
    if (accel == 0) accel = pumpAccel;
    
    // find an unused controller
    StepControl<>* ctrl = NULL;
    for (byte i = 0; i < PUMP_CONTROLLERS; i++) {
        if (! allPumpControllers[i]->isRunning()) {
            ctrl = allPumpControllers[i];
            break;
        }
    }
    if (ctrl == NULL) {
        sendError("too busy");
        return;
    }
    
    enablePumps();
    allPumps[pumpNum]->setPosition(0);
    allPumps[pumpNum]->setTargetAbs(steps);
    allPumps[pumpNum]->setMaxSpeed(speed);
    allPumps[pumpNum]->setAcceleration(accel);
    pumpControllers[pumpNum] = ctrl;
    pumpDir = dir;
    ctrl->moveAsync(*allPumps[pumpNum]);
    
    sendOK();
    sendPumpRunning(pumpNum);
}

void cmdPumpHalt(char* str) {
    byte pumpNum;
    pumpNum = readInt(&str);
    
    if (pumpNum >= PUMPS) {
        sendError("invalid pump");
        return;
    }
    if (pumpControllers[pumpNum]) {
        pumpControllers[pumpNum]->stopAsync();
    }
    sendOK();
}

void cmdPumpFlush(char* str) {
    if (str[0] == 0) {
        // stop flushing
        if (pumpsFlushing) {
            pumpCtrl0.stopAsync();
        }
        sendOK();
            
    } else {
        // start flushing
        if (pumpsFlushing) {
            sendError("pumps are already flushing");
            return;
        }
        if (pumpsAreRunning()) {
            sendError("pumps are running");
            return;
        }
        
        Stepper* pumps[PUMPS] = {NULL};
        
        for (int i = 0; i < PUMPS; i++) {
            unsigned p = readUInt(&str);
            if (p >= PUMPS) {
                sendError("invalid pump");
                return;
            }
            pumps[i] = allPumps[p];
            pumps[i]->setAcceleration(pumpAccel);
            pumps[i]->setMaxSpeed(pumpSpeed);
            pumpControllers[p] = &pumpCtrl0;
            sendPumpRunning(p);
            
            if (! readDelim(&str)) break;
        }
        
        enablePumps();
        pumpCtrl0.rotateAsync(pumps);
        
        pumpsFlushing = true;
        sendOK();
    }
}

void cmdPumpSpeed(char* str) {
    int speed = readInt(&str);
    if ((speed < PUMP_MIN_SPEED) || (speed > PUMP_MAX_SPEED)) {
        sendError("invalid speed");
        return;
    }
    pumpSpeed = speed;
    sendOK();
}

void cmdPumpAcceleration(char* str) {
    unsigned accel = readUInt(&str);
    if ((accel < PUMP_MIN_ACCEL) || (accel > PUMP_MAX_ACCEL)) {
        sendError("invalid acceleration");
        return;
    }
    pumpAccel = accel;
    sendOK();
}

void cmdPumpStatus() {
    send("speed: ");
    sendInt(pumpSpeed);
    sendChar('\n');
    
    send("acceleration: ");
    sendInt(pumpAccel);
    sendChar('\n');
    
    for (byte i = 0; i < PUMPS; i++) {
        sendChar('P');
        sendInt(i);
        send(": ");
        if (pumpControllers[i]) send("running");
        sendChar('\n');
    }
    
    for (byte i = 0; i < PUMP_CONTROLLERS; i++) {
        send("PC");
        sendInt(i);
        send(": ");
        if (allPumpControllers[i]->isOk()) send("OK");
        else send("ERR");
        if (allPumpControllers[i]->isRunning()) send(",running");
        sendChar('\n');
    }
    
    sendOK();
}

// =========== Other stuff

int readInt(char** strPtr) {
    bool neg = false;
    int i = 0;
    char* str = *strPtr;
    if (*str == '-') {
        str++;
        neg = true;
    }
    while ((*str >= '0') && (*str <= '9')) {
        i = (i * 10) + (*str - '0');
        str++;
    }
    *strPtr = str;
    return neg ? -i : i;
}

unsigned readUInt(char** strPtr) {
    unsigned i = 0;
    char* str = *strPtr;
    while ((*str >= '0') && (*str <= '9')) {
        i = (i * 10) + (*str - '0');
        str++;
    }
    *strPtr = str;
    return i;
}

unsigned readHex(char** strPtr) {
    unsigned i = 0;
    char* str = *strPtr;
    while (1) {
        if ((*str >= '0') && (*str <= '9')) {
            i = (i << 4) + (*str - '0');
            str++;
        } else if ((*str >= 'a') && (*str <= 'f')) {
            i = (i << 4) + (*str - 'a');
            str++;
        } else if ((*str >= 'A') && (*str <= 'F')) {
            i = (i << 4) + (*str - 'A');
            str++;
        } else
            break;
    }
    *strPtr = str;
    return i;
}

bool readDelim(char** strPtr) {
    return readDelim(strPtr, ',');
}

bool readDelim(char** strPtr, char delim) {
    char* str = *strPtr;
    if (*str == delim) {
        str++;
        *strPtr = str;
        return true;
    } else {
        return false;
    }
}

void send(const char* str) {
    Serial.print(str);
}

void sendChar(char ch) {
    Serial.print(ch);
}

void sendInt(int i) {
    Serial.print(i);
}

void sendOK() {
    send("OK\n");
}

void sendError(const char* msg) {
    sendChar('!');
    send(msg);
    sendChar('\n');
}

void sendMessage(const char* msg) {
    sendChar('#');
    send(msg);
    sendChar('\n');
}

void sendPumpRunning(byte pumpNum) {
    send("*PR");
    sendInt(pumpNum);
    sendChar('\n');
}

void sendPumpStopped(byte pumpNum) {
    send("*PS");
    sendInt(pumpNum);
    sendChar('\n');
}

bool pumpsAreRunning() {
    return pumpCtrl0.isRunning() ||
           pumpCtrl1.isRunning() ||
           pumpCtrl2.isRunning() ||
           pumpCtrl3.isRunning();
}
