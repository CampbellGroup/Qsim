#include <SPI.h>
const int clk = 52;
const int SPO = 51;
const int LD = 24;
const int PR = 25;
void setup()
{
  pinMode(clk, OUTPUT);
  pinMode(SPO, OUTPUT);
  pinMode(LD, OUTPUT);
  pinMode(PR, OUTPUT);
  digitalWrite(clk, LOW);
  digitalWrite(LD, LOW);
  digitalWrite(PR, LOW);
  digitalWrite(PR, HIGH);
}

void loop()
{
  for (int j = 0; j<3; j++)
   {
     digitalWrite(clk, HIGH);
     digitalWrite(SPO, LOW);
     digitalWrite(clk, LOW);
   }
    digitalWrite(SPO, HIGH);
    digitalWrite(clk, HIGH);
    digitalWrite(clk, LOW);
    digitalWrite(SPO, LOW);
     
  for (int i = 0; i<8; i++)
   {
    digitalWrite(SPO,HIGH);
    digitalWrite(clk, HIGH);
    digitalWrite(clk, LOW);
    digitalWrite(SPO, LOW); 
   }
   digitalWrite(LD,HIGH);
   digitalWrite(clk,HIGH);
   digitalWrite(clk,LOW);
   digitalWrite(LD, LOW);
   delay(1000);
   
   // turn to max value
   
  for (int j = 0; j<3; j++)
   {
     digitalWrite(SPO, LOW);
     digitalWrite(clk, HIGH);
     digitalWrite(clk, LOW);
   }
    digitalWrite(SPO, HIGH);
    digitalWrite(clk, HIGH);
    digitalWrite(clk, LOW);
    digitalWrite(SPO, LOW);
     
  for (int i = 0; i<8; i++)
   {
    digitalWrite(SPO,LOW);
    digitalWrite(clk, HIGH);
    digitalWrite(clk, LOW);
   }
   digitalWrite(LD,HIGH);
   digitalWrite(clk,HIGH);
   digitalWrite(clk,LOW);
   digitalWrite(LD, LOW);
   delay(1000);
 }
