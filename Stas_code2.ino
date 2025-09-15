/*************
  Blynk is a platform with iOS and Android apps to control
  ESP32, Arduino, Raspberry Pi and the likes over the Internet.
  You can easily build mobile and web interfaces for any
  projects by simply dragging and dropping widgets.

    Downloads, docs, tutorials: https://www.blynk.io
    Sketch generator:           https://examples.blynk.cc
    Blynk community:            https://community.blynk.cc
    Follow us:                  https://www.fb.com/blynkapp
                                https://twitter.com/blynk_app

  Blynk library is licensed under MIT license
  This example code is in public domain.

 *************
  This example runs directly on ESP8266 chip.

  NOTE: This requires ESP8266 support package:
    https://github.com/esp8266/Arduino

  Please be sure to select the right ESP8266 module
  in the Tools -> Board menu!

  Change WiFi ssid, pass, and Blynk auth token to run :)
  Feel free to apply it to any other example. It's simple!
 *************/

/* Comment this out to disable prints and save space */
#define BLYNK_PRINT Serial

/* Fill in information from Blynk Device Info here */
//#define BLYNK_TEMPLATE_ID           "TMPxxxxxx"
//#define BLYNK_TEMPLATE_NAME         "Device"
//#define BLYNK_AUTH_TOKEN            "YourAuthToken"

#define BLYNK_TEMPLATE_ID           "TMPL4QaHDj59p"
#define BLYNK_TEMPLATE_NAME         "Quickstart Template"
#define BLYNK_AUTH_TOKEN            "QUd9Im1Onl_7YRcT8_FHOlnRjqf-b52O"

#include <ESP8266WiFi.h>
#include <BlynkSimpleEsp8266.h>

// Your WiFi credentials.
// Set password to "" for open networks.
char ssid[] = "IS-WIFI";
char pass[] = "RadinSEC600";

#include <Servo.h>

Servo kleshnya;  
Servo kist_rotary;
Servo kist_bend;
Servo shoulder;
Servo collarbone;
Servo guohu;

void setup()
{
  // Debug console
  Serial.begin(9600);
  Blynk.begin(BLYNK_AUTH_TOKEN, ssid, pass);

  pinMode(2, OUTPUT); // Initialise digital pin 2 as an output pin
  
  kleshnya.attach(16);  // attaches the servo on GIO2 to the servo object
  kist_rotary.attach(5);
  kist_bend.attach(4);
  shoulder.attach(0);
  collarbone.attach(14);
  guohu.attach(12);
}

void loop()
{
  Blynk.run();
}

BLYNK_WRITE(V0) // Executes when the value of virtual pin 0 changes
{
  if(param.asInt() == 1)
  {
    // execute this code if the switch widget is now ON
    digitalWrite(2,LOW);  // Set digital pin 2 HIGH
  }
  else
  {
    // execute this code if the switch widget is now OFF
    digitalWrite(2,HIGH);  // Set digital pin 2 LOW    
  }
}

BLYNK_WRITE(V1) // Слайдер у Blynk
{
  int angle = param.asInt(); // 0–180 градусів
  kleshnya.write(angle);
}
BLYNK_WRITE(V2) // Слайдер у Blynk
{
  int angle = param.asInt(); // 0–180 градусів
  kist_rotary.write(angle);
}
BLYNK_WRITE(V3) // Слайдер у Blynk
{
  int angle = param.asInt(); // 0–180 градусів
  kist_bend.write(angle);
}
BLYNK_WRITE(V4) // Слайдер у Blynk
{
  int angle = param.asInt(); // 0–180 градусів
  shoulder.write(angle);
}
BLYNK_WRITE(V5) // Слайдер у Blynk
{
  int angle = param.asInt(); // 0–180 градусів
  collarbone.write(angle);
}
BLYNK_WRITE(V6) // Слайдер у Blynk
{
  int angle = param.asInt(); // 0–180 градусів
  guohu.write(angle);
}
