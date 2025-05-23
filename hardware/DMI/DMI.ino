#include <MovingAverageFilter.h>
#include <ADCTouch.h>

#define OFFSET_ENERGY_DELTA_THRESH 0.3
#define OFFSET_SETTLE_TIME 40 // in ms

int rawPiezoInput;
float filteredPizeoInput;
float previousPiezoInput; // set really big just so whatever initial values are don't trigger an onset

MovingAverageFilter pizeoFilter(10);
MovingAverageFilter pressureFilter(20);

bool onsetFlag = true; // wait for it to settle so it doesn't send one on boot
unsigned long onsetTime;
bool detectedOnset = false; 

float EMA_a = 0.3;    //initialization of EMA alpha
int EMA_S = 0;        //initialization of EMA S
float highpassValue = 0;

int raw_avg_pressure;
int filtered_avg_pressure;

int capacitiveTouchRef, capacitiveTouchVal;
bool isCapacitiveTouch = false;
bool previousCapacitiveTouch = false;

bool isThereOnset(float threshold) {
      if (filteredPizeoInput - previousPiezoInput > threshold) {
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
  capacitiveTouchRef = ADCTouch.read(A1);
  previousPiezoInput = EMA_S;
  Serial.print("time (ms)");
  Serial.print(',');
  Serial.print("onset_detection");
  Serial.print(',');
  Serial.println("capacitive_detection");
}

void loop() {
  // put your main code here, to run repeatedly:
  rawPiezoInput = analogRead(A0);  // read the input pin
  raw_avg_pressure = (analogRead(A2) + analogRead(A3) + analogRead(A4) + analogRead(A5)) / 4;
  filtered_avg_pressure = pressureFilter.process(raw_avg_pressure) - 600; // evil magic number, quick band-aid to make pressure settle around 0
  EMA_S = (EMA_a*rawPiezoInput) + ((1-EMA_a)*EMA_S);
  highpassValue = constrain(rawPiezoInput - EMA_S, 0, 100); 
  filteredPizeoInput = pizeoFilter.process(highpassValue);

//   onset stuff!
  detectedOnset = isThereOnset(OFFSET_ENERGY_DELTA_THRESH);

  capacitiveTouchVal = ADCTouch.read(A1);
  capacitiveTouchVal -= capacitiveTouchRef;
  isCapacitiveTouch = capacitiveTouchVal > 40;

  Serial.print(millis());
  Serial.print(',');
  
  if (detectedOnset && !onsetFlag && filtered_avg_pressure < 100) {
    onsetFlag = true;
    onsetTime = millis();
    Serial.print(true);
  } else {
    Serial.print(false);
  }

  
  
//  Serial.println(filteredPizeoInput);
  Serial.print(',');
  if (isCapacitiveTouch && !previousCapacitiveTouch) {
    Serial.println(true); 
  } else {
    Serial.println(false); 
  }

  previousCapacitiveTouch = isCapacitiveTouch;


  if (!detectedOnset && onsetFlag) {
    if (millis() - onsetTime > OFFSET_SETTLE_TIME) {
          onsetFlag = false;
    }
    

  }

  previousPiezoInput = filteredPizeoInput;

}
