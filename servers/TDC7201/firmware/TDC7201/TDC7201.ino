int CSB1 = 2; 
int SCLK = 3;
int DIN = 4;
int DOUT1 = 5;
int LED = 13;

byte address = 0; 
byte write_data = 0;
byte read_data = 0;


void setup() {

  Serial.begin(9600);

  // Set all pins to output mode.
  pinMode(CSB1, OUTPUT);  
  pinMode(SCLK, OUTPUT);
  pinMode(DIN, INPUT);
  pinMode(DOUT1, OUTPUT);
  pinMode(LED, OUTPUT);

  // Initialize pin values.
  digitalWrite(CSB1, LOW);
  digitalWrite(SCLK, LOW);
  digitalWrite(DIN, LOW);

}

void writeRegister(byte address, byte data){

  digitalWrite(CSB1, LOW);
  
  for (int j=0; j<8; j++) 
   {
     boolean currentchanbit = address & 0b10000000;
     address = address << 1;
     digitalWrite(DOUT1, currentchanbit);
     digitalWrite(SCLK, HIGH);
     digitalWrite(SCLK, LOW);
   }
  for (int i = 0; i<8; i++)
   {
    boolean currentvaluebit = data & 32768;
    data = data << 1;
    digitalWrite(DOUT1, currentvaluebit);
    digitalWrite(SCLK, HIGH);
    digitalWrite(SCLK, LOW); 
    
   }
  digitalWrite(CSB1, HIGH);
}


void loop()
{
  while(Serial.available() < 2);  
  address = Serial.read();
  write_data = Serial.read();
  writeRegister(address, write_data);
 }
 
