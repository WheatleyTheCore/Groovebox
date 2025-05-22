#include <MovingAverageFilter.h>

#define OFFSET_ENERGY_DELTA_THRESH 8
#define OFFSET_SETTLE_TIME 60 // in ms

int rawPiezoInput;
float filteredPizeoInput;
float previousPiezoInput; // set really big just so whatever initial values are don't trigger an onset

MovingAverageFilter pizeoFilter(3);
MovingAverageFilter pressureFilter(20);

bool onsetFlag = true; // wait for it to settle so it doesn't send one on boot
unsigned long onsetTime;
bool detectedOnset = false; 

float EMA_a = 0.3;    //initialization of EMA alpha
int EMA_S = 0;        //initialization of EMA S
float highpassValue = 0;

int raw_avg_pressure;
int filtered_avg_pressure;

bool isThereOnset(float threshold) {
      if (abs(filteredPizeoInput - previousPiezoInput) > threshold) {
        return true;
      } else {
        return false;
      }
}

void setup() {
  // put your setup code here, to run once:
  pinMode(A0, INPUT);
  pinMode(A2, INPUT);
  pinMode(A3, INPUT);
  pinMode(A4, INPUT);
  pinMode(A5, INPUT);
  Serial.begin(9600);
  EMA_S = analogRead(A0);     //set EMA S for t=1
  previousPiezoInput = EMA_S;
}

void loop() {
  // put your main code here, to run repeatedly:
  rawPiezoInput = analogRead(A0);  // read the input pin
  raw_avg_pressure = (analogRead(A2) + analogRead(A3) + analogRead(A4) + analogRead(A5)) / 4;
  filtered_avg_pressure = pressureFilter.process(raw_avg_pressure) - 318; // evil magic number, quick band-aid to make pressure settle around 0
  EMA_S = (EMA_a*rawPiezoInput) + ((1-EMA_a)*EMA_S);
  highpassValue = rawPiezoInput - EMA_S; 
  filteredPizeoInput = pizeoFilter.process(highpassValue);

//   onset stuff!
  detectedOnset = isThereOnset(OFFSET_ENERGY_DELTA_THRESH);
  
  
  if (detectedOnset && !onsetFlag && filtered_avg_pressure < 20) {
    onsetFlag = true;
    onsetTime = millis();
    Serial.print(100);
  } else {
    Serial.print(0);
  }

  Serial.print(" ");
  Serial.println(filtered_avg_pressure); 



  if (!detectedOnset && onsetFlag) {
    if (millis() - onsetTime > OFFSET_SETTLE_TIME) {
          onsetFlag = false;
    }
    

  }

  previousPiezoInput = filteredPizeoInput;

}
