/*
Stepper Gimbal for RPLidar Proof of Concept
THT 2/4/20
*/

#include <Wire.h>
#include <Adafruit_MotorShield.h>
//#include "utility/Adafruit_PWMServoDriver.h"

// Limit Switches
#define panSwitch 9
#define tiltSwitch 10

// Motor Shield 
Adafruit_MotorShield AFMS = Adafruit_MotorShield();
Adafruit_StepperMotor *TiltMotor = AFMS.getStepper(200, 1);
Adafruit_StepperMotor *PanMotor = AFMS.getStepper(200, 2);


String inString = "";    // string to hold input ..... Don't know if needed 

void home(){
  Serial.print("Homing... ");
  while(digitalRead(panSwitch) != HIGH){
    PanMotor->step(1,BACKWARD,MICROSTEP);
  }
  Serial.print("... ");
  // while(digitalRead(tiltSwitch) != HIGH){
  //   TiltMotor->step(1,BACKWARD,MICROSTEP)
  // }
  Serial.println("...Homed");
}

void setup() {
  Serial.begin(115200);
  AFMS.begin();
  
  TiltMotor->setSpeed(10);
  PanMotor->setSpeed(10);

  home();
}

void loop() {
  static int tilt = 0;
  static int pan = 0;
  
  while (Serial.available() > 0) {
    inString = Serial.readString();
    pan=inString.toInt();
    if(pan!=0){
      float angle = pan*1.8;
      Serial.print("Panning: "); Serial.print(pan); Serial.print(" steps"); Serial.print("\t"); Serial.print(angle); Serial.println(" degrees");
      // Pan Stepper
      if(pan<0){
        // Serial.println("BACKWARD");
        PanMotor->step(abs(pan), BACKWARD, MICROSTEP);
        pan=0;
      }
      else{
        // Serial.println("FORWARD");
        PanMotor->step(pan, FORWARD, MICROSTEP);
        pan=0;
      } 
    }
    // clear the string for new input:
    inString = "";
  }
}

