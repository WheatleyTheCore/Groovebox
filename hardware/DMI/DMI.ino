#include <MovingAverageFilter.h>

#define OFFSET_ENERGY_DELTA_THRESH 1
#define OFFSET_SETTLE_TIME 50 // in cycles

int rawInput;
float filteredInput;
float previousValue; // set really big just so whatever initial values are don't trigger an onset
MovingAverageFilter movingAverageFilter(3);
bool bangFlag = true; // wait for it to settle so it doesn't send one on boot
bool detectedOnset = false; 
float EMA_a = 0.3;    //initialization of EMA alpha
int EMA_S = 0;        //initialization of EMA S
float highpassValue = 0;
int bangLowCount = 0;

bool isThereOnset(float threshold) {
      if (abs(filteredInput - previousValue) > threshold) {
        return true;
      } else {
        return false;
      }
}

void setup() {
  // put your setup code here, to run once:
  pinMode(A0, INPUT);
  Serial.begin(9600);
  EMA_S = analogRead(A0);     //set EMA S for t=1
  previousValue = EMA_S;
}

void loop() {
  // put your main code here, to run repeatedly:
  rawInput = analogRead(A0);  // read the input pin
  EMA_S = (EMA_a*rawInput) + ((1-EMA_a)*EMA_S);
  highpassValue = rawInput - EMA_S; 
  filteredInput = movingAverageFilter.process(highpassValue);

//   onset stuff!
  detectedOnset = isThereOnset(OFFSET_ENERGY_DELTA_THRESH);
  
  
  if (detectedOnset && !bangFlag) {
    Serial.println("Bang!");
    bangFlag = true;
  }

  if (!detectedOnset && bangFlag) {
    bangLowCount++;
    if (bangLowCount > OFFSET_SETTLE_TIME) {
          bangFlag = false;
          bangLowCount = 0;
    }
    

  }

  previousValue = filteredInput;

}
