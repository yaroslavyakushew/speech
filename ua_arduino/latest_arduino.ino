#include <Servo.h>
#include <Schedule.h>
 


//unsigned long now = millis();

int interval = 60;
bool stop1 = false;
int curServo = 0;

class MyServo {
  public:
    Servo servo;
    int angle;
    int max_angle;
    int min_angle;
    int pin;
    int delay_ms;
    String flag; 
    unsigned long prev = 0;
    bool run1 = false;
   
    MyServo(int p, int min_a, int max_a, int d, String f) {
      pin = p;
      min_angle = min_a;
      max_angle = max_a;
      angle = min_angle;
      delay_ms = d;
      flag = f;
    }

    void attach1() {
      servo.attach(pin);
      servo.write(angle);
    }

    void set_angle(int a) {
      angle = constrain(a, min_angle, max_angle);
      servo.write(angle);
    }

 void movement(bool reverse) {
  Serial.println("Movement started");
  if (!run1) { return; }

  if (millis() - prev < delay_ms) {
    Serial.println(millis() - prev);
    schedule_function([this, reverse]() {
      this->movement(reverse);
    });
    return;
  }

  prev = millis();

  if (!reverse) {
    if (angle >= max_angle) { run1 = false; Serial.println("run false"); return; }
    angle++;
  } else {
    if (angle <= min_angle) { run1 = false; Serial.println("run false"); return; }
    angle--;
  }

  if (stop1) { run1 = false;
  return; }

  set_angle(angle);
  Serial.println(angle);

  schedule_function([this, reverse]() {
    this->movement(reverse);
  });
}


    void up() {
      stop1 = false;
      run1 = true;
      movement(false);
    }

    void down() {
      stop1 = false;
      run1 = true;
      movement(true);
    }
};

// !create a list of classes and insert all existing classes into it!
MyServo kleshnya(16, 0, 160, 15, "клешня"); //Стискати кулак
MyServo kist_rotary(5, 0, 180, 15, "вфафва"); //Крутить кулачок
MyServo kist_bend(4, 0, 100, 15, "внутрішній лікоть"); //2 изгиб локтя
MyServo shoulder(0, 110, 180, 15, "лікоть"); //Локоть
MyServo collarbone(14, 0, 180, 15, "база"); //Основание

MyServo guohu(12, 0, 90, 30, "плече"); //?

MyServo* classList[] = {&kleshnya, &kist_rotary, &kist_bend, &shoulder, &collarbone, &guohu};
void (*softReset) (void) = 0;

void voiceCommand(String word1) {
   if (word1 == "рука вгору") {
         schedule_function(+[](){guohu.up();});
         schedule_function(+[](){shoulder.up();});
         schedule_function(+[](){kist_bend.up();});
   }
   else if (word1 == "рука вниз"){
    schedule_function(+[](){guohu.down();});
    schedule_function(+[](){shoulder.down();});
    schedule_function(+[](){kist_bend.down();});
   }
   
   for (auto i: classList){
       if (word1 == i.flag) {
           curServo = i.pin
       }
    }
   
   else if (word1 == "стоп"){
      stop1 = true;
   }
   else if (word1 == "вправо"){
      kist_rotary.up(); 
   }
   else if (word1 == "вліво"){
      kist_rotary.down();
   }
   else if (word1 == "вгору"){
    Serial.println("up");
     for (auto obj: classList){
        if (curServo == obj->pin){
           schedule_function([obj](){obj->up();});
        }
      }
   }
   else if (word1 == "вниз"){
     Serial.println("down");
     for (auto obj: classList){
        if (curServo == obj->pin){
           schedule_function([obj](){obj->down();});
        }
      }
   }
}
  

void setup() {
  Serial.begin(9600);
  for (int i = 0; i < sizeof(classList) / sizeof(classList[0]); i++) {
    classList[i]->attach1();
  }
  
  shoulder.set_angle(0);
  kist_bend.set_angle(0);
  kleshnya.set_angle(0);
  guohu.set_angle(0);
  kist_rotary.set_angle(90);
}

String text = "";
void loop() {
  if (Serial.available()){
     text = Serial.readString();
     text.trim();
     text.toLowerCase();
     Serial.println(text);
     int count = 0;
     String words[10];
     int start1 = 0;
     int index = text.indexOf('\n');
     while (index != -1){
        words[count++] = text.substring(start1, index);
        start1 = index + 1;
        index = text.indexOf('\n', start1);
      }
      words[count++] = text.substring(start1);
     Serial.print("Reading: ");
     Serial.println(text);
     for (auto i: words){
       voiceCommand(i);
      }
     text = "";
   }
   
}
