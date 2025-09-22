/* Sweep
  by BARRAGAN <http://barraganstudio.com>
  This example code is in the public domain.

  modified 28 May 2015
  by Michael C. Miller
  modified 8 Nov 2013
  by Scott Fitzgerald

  http://arduino.cc/en/Tutorial/Sweep
*/

#include <Servo.h>

Servo kleshnya;  // create servo object to control a servo
// twelve servo objects can be created on most boards
Servo kist_rotary;
Servo kist_bend;
Servo shoulder;
Servo collarbone;
Servo guohu;

bool stop = false;
bool run = false;


void movement(int &angle, bool reverse, int max_angle, int min_angle){
    int time_a;
    if (reverse == false) {time_a = max_angle - angle;}
    else {time_a = angle - min_angle;};

    for (int i = 0; i < time_a; i++){
      run = true;
      if (stop) {break;};
      if (reverse == false) {angle += 1;}
      else {time_a = angle - min_angle;};
    }
    run = false;
  }

//дістати з класів змінну кута
// створити список класів і вставити туди всі існуючі класи
void setup() {
  kleshnya.attach(16);  // attaches the servo on GIO2 to the servo object
  kist_rotary.attach(5);
  kist_bend.attach(4);
  shoulder.attach(0);
  collarbone.attach(14);
  guohu.attach(12);
}

void loop() {
  kleshnya.write(0);
  kist_rotary.write(0);
}

//Як відпавляти файли на гітхаб?
//1. Спочатку перейти у папку гітхаб проекта (cd speech прописати у консолі)
//2. Далі додати всі файли у гіті (git add . у консолі)
//3. Прийняти зміни з коментарем (git commit -m "Your comment")
//4. Відправити зміни на гітхаб (git push)

//Як приймати файли з гітхабу?
//1. Спочатку перейти у папку гітхаб проекта (cd speech прописати у консолі)
//2. Отримати зміни з гітхаб репозиторію (git pull)
