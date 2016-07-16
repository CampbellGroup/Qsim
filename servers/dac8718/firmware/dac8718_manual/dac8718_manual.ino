int CS = 8; 
int SCLK = 9;
int SDO = 10;
int LDAC = 11;


int CLR = 2;
int RESET = 3;

int USB_BTC = 4;
int RSTSEL = 7;
int WAKEUP = 5;

int GPIO0 = 6;
int GPIO1 = 1;


byte chanByte = 0; 
word value = 0; 

void setup() {
  
  pinMode(CS, OUTPUT);  
  pinMode(SCLK, OUTPUT);
  pinMode(SDO, OUTPUT);
  pinMode(LDAC, OUTPUT);
  
  pinMode(CLR, OUTPUT);
  pinMode(RESET, OUTPUT);

  pinMode(USB_BTC, OUTPUT);
  pinMode(RSTSEL, OUTPUT);
  pinMode(WAKEUP, OUTPUT);
  
  pinMode(GPIO0, OUTPUT);
  pinMode(GPIO1, OUTPUT);


  digitalWrite(CS, LOW);
  digitalWrite(SCLK, LOW);
  digitalWrite(SDO, HIGH);
  digitalWrite(LDAC, LOW);

  digitalWrite(CLR, HIGH);
  digitalWrite(RESET, HIGH);

  digitalWrite(USB_BTC, LOW);
  digitalWrite(RSTSEL, LOW);
  digitalWrite(WAKEUP, HIGH);
  
  digitalWrite(GPIO0, HIGH);
  digitalWrite(GPIO1, HIGH);

}

void writeRegister(byte address, word data){

  digitalWrite(CS, LOW);
  
  for (int j=0; j<8; j++) 
   {
     boolean currentchanbit = address & 0b10000000;
     address = address << 1;
     digitalWrite(SDO, currentchanbit);
     digitalWrite(SCLK, HIGH);
     digitalWrite(SCLK, LOW);
   }
     /*
     this next loop writes to the dac channel the output voltage from min (0b00000000) to max (0b11111111)
     */
  for (int i = 0; i<16; i++) // hard coded output 0b11111111 (max voltage)
   {
    boolean currentvaluebit = data & 32768;
    data = data << 1;
    digitalWrite(SDO, currentvaluebit);
    digitalWrite(SCLK, HIGH);
    digitalWrite(SCLK, LOW); 
    
   }
  digitalWrite(CS, HIGH);
}


void loop()
{
  
  chanByte = 0b00001001;
  value = 0x0;

   writeRegister(chanByte, value);
   delay(1000);
   value = 0xFFFF;
   writeRegister(chanByte, value);
   delay(1000);
   
 }
