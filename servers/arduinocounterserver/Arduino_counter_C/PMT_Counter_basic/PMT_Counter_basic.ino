/* PMT counter basic v 1.0
 */
#include <FreqCount.h>

void setup() {
  Serial.begin(57600);
  FreqCount.begin(100);
}

void loop() {
  if (FreqCount.available()) {
    unsigned long count = FreqCount.read();
    Serial.println(count, DEC);
  }
}

