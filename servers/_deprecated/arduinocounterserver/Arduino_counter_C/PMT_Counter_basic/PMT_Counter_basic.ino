#include <FreqCount.h>
unsigned long gatetime = 100; // in ms 
unsigned long count = 0;
unsigned long rate = 0;

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(10);
  FreqCount.begin(gatetime);
}

void loop() {
  if (Serial.available()){
    gatetime = Serial.parseFloat();
    FreqCount.begin(gatetime);
  }
  if (FreqCount.available()) {
    count = FreqCount.read();
    Serial.println(count);
  }
}

