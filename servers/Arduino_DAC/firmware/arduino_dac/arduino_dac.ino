/*
Creates bytes to read in on serial commands
*/
byte chan = 0;
byte value = 0;

/*
define clock pin, Serial Pin Output, Load DAC pin and Preset input pin respectively 
*/
const int clk = 52;
const int SPO = 51;
const int LD = 24;
const int PR = 25;
void setup()
{
/*
Set baudrate for serial communication
*/
  Serial.begin(57600);
/*
All pins are outputs from arduino to DAC
*/
  pinMode(clk, OUTPUT);
  pinMode(SPO, OUTPUT);
  pinMode(LD, OUTPUT);
  pinMode(PR, OUTPUT);
  
/*
All pins are set to low except preset (High means DAC ready for data)
*/
  digitalWrite(clk, LOW);
  digitalWrite(LD, LOW);
  digitalWrite(PR, LOW);
  digitalWrite(PR, HIGH);
}

void loop()
{
  while(Serial.available() < 2); //wait for two bytes to be in the buffer
  chan = Serial.read();
  value = Serial.read();
  /* 
  The following iterates over the 4 most significant bits of input number in binary
  and output them to pin SPO. This specifies the channel from 1-8. Allowed values are 0b0001 to (DAC A) to 0b1000 (DAC H) 
  */

  for (int j = 0; j<4; j++) //iterate over nibble that is channel number and write it
   {
     boolean currentchanbit = chan & 9; // This zeros out the byte to the left of bit 4 and leaves bit 4 unchanged
     currentchanbit  = currentchanbit >> 3;//this chops of the right three bits leaving just one bit (bit 4)
     chan = chan << 1;// shifts channel to the left one so the next bit in the 4 slot was the old 3 bit
     digitalWrite(SPO,currentchanbit);//writes the current bit
     digitalWrite(clk, HIGH);// The data from SPO is read when clock is HIGH so set SPO before clock pulse
     digitalWrite(clk, LOW);
     digitalWrite(SPO, LOW);
   }
     /*
     this next loop writes to the dac channel the output voltage allowed values: min (0b00000000) to max (0b11111111)
     */
  for (int i = 0; i<8; i++) //iterate over value byte
   {
    boolean currentvaluebit = value & 255;// after the bit shift the byte grows by one bit, this chops it off
    currentvaluebit = currentvaluebit >> 7;// shifts right seven bits away so only left with the 8 bit
    value = value << 1;//shifts value to the left so 7 bit is now in 8 bit slot
    digitalWrite(SPO,currentvaluebit);//writes the old 8 bit
    digitalWrite(clk, HIGH);
    digitalWrite(clk, LOW);
    digitalWrite(SPO, LOW); 
   }
   digitalWrite(LD,HIGH);//LD loads the data into the dac registry
   digitalWrite(clk,HIGH);
   digitalWrite(clk,LOW);
   digitalWrite(LD, LOW);
 }
