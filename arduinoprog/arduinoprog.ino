#include <Wire.h>
#include <math.h>
#include "rgb_lcd.h"
#define LDR A1  // composante photorésistance sur la pin A1
#define LDC A3  // composante capteur de température sur la pin A3
#define POT A2  // composant potentiometre
const int B = 4275;               // B value of the thermistor
const int R0 = 100000;   
const int ledrouge = 3;
const int ledbleu = 7;
const int ledjaune = 5;
int out;
rgb_lcd lcd;
 
const int colorR = 128;
const int colorG = 128;
const int colorB = 128;
/*
Code 
3 = Allumer la led rouge (chauffage)
4 = Eteindre la led rouge (chauffage)
7 = Allumer la led bleu (fontaine)
8 = Eteindre la led bleu (fontaine)
5 = Allumer la led jaune (lumiere)
6 = Eteindre la led jaune (lumiere)
(LDR = Capteur de lumière)
9 = Récuperer la valeur de la lumière (du capteur)
10 = Récuperer la valeur du chauffage (du capteur)
Afficher:
Statut led chauffage
Statut led fontaine
Statut led lumière 
Capt temp
Capt de lumière

*/

void setup(){
      // set up the LCD's number of columns and rows:
    lcd.begin(16, 2);
 
    lcd.setRGB(colorR, colorG, colorB);
 
    // Print a message to the LCD.
    lcd.print("Init ...");
 
    delay(1000);
  Serial.begin(9600);
  //digitalWrite(ledrouge,HIGH);
  pinMode(ledrouge, OUTPUT);
  pinMode(ledbleu, OUTPUT);
  pinMode(ledjaune, OUTPUT);
  pinMode(LDR, INPUT);
  digitalWrite(13, HIGH);
  Serial.println("Ready");
  }


void loop() {
    int light = analogRead(LDR); // Lit la valeur du capteur de luminosité
    float R = 1023.0/analogRead(LDC)-1.0;
    R = R0*R;
    float tempera = 1.0/(log(R/R0)/B+1/298.15)-273.15;
    Serial.print(tempera); // Envoie la température via la communication série
    Serial.print(" ");
    Serial.println(light);
    int potent = analogRead(POT);
    int nombre = 0; // wait for serial port to connect.
    if (Serial.available()){ 
    //s'il y a des données qui arrivent  
        int nombre = Serial.parseInt();//Lecture d'un entier sur le tampon série    
        if (nombre==3){digitalWrite(ledrouge,HIGH);}  
        if (nombre==4){digitalWrite(ledrouge,LOW);}  
        if (nombre==7){digitalWrite(ledbleu,HIGH);} 
        if (nombre==8){digitalWrite(ledbleu,LOW);}  
        if (nombre==5){digitalWrite(ledjaune,HIGH);}  
        if (nombre==6){digitalWrite(ledjaune,LOW);}
        if(nombre==9){
          out = analogRead(LDR);
          Serial.println(out);
        }
        if(nombre==10){
          float R = 1023.0/analogRead(LDC)-1.0;
          R = R0*R;
          float temperature = 1.0/(log(R/R0)/B+1/298.15)-273.15;
          Serial.println(temperature);
        }
      } 
      Serial.flush();
      if(potent<205){
        lcd.setCursor(0, 0);
        lcd.clear();
        lcd.print("Etat de la lumiere");
        lcd.setCursor(0, 1);
        if(digitalRead(ledjaune) == HIGH){
          lcd.setRGB(0, 255, 0);
          lcd.print("ON");
          }
          else{
            lcd.setRGB(255, 0, 0);
            lcd.print("OFF");
            
        }
        }
      if(potent>206 and potent<410){
        lcd.setCursor(0, 0);
        lcd.clear();
        lcd.print("Etat du chauffage");
        lcd.setCursor(0, 1);
        if(digitalRead(ledrouge) == HIGH){
          lcd.setRGB(0, 255, 0);
          lcd.print("ON");
          }
          else{
             lcd.setRGB(255, 0, 0);
            lcd.print("OFF");
        }
        
        }

        if(potent>411 and potent<615){
        lcd.setCursor(0, 0);
        lcd.clear();
        lcd.print("Etat de la fontaine");
        lcd.setCursor(0, 1);
        if(digitalRead(ledbleu) == HIGH){
          lcd.setRGB(0, 255, 0);
          lcd.print("ON");
          }
          else{
             lcd.setRGB(255, 0, 0);
            lcd.print("OFF");
        }
        
        }

        if(potent>616 and potent<821){
        lcd.setCursor(0, 0);
        lcd.clear();
        lcd.print("Température");
        lcd.setRGB(colorR, colorG, colorB);
        lcd.setCursor(0, 1);
        
        float R = 1023.0/analogRead(LDC)-1.0;
        R = R0*R;
 
        float temperature = 1.0/(log(R/R0)/B+1/298.15)-273.15;
        lcd.print(temperature);

        }
        if(potent>822 and potent<1027){
        lcd.setCursor(0, 0);
        lcd.clear();
        lcd.print("Luminosité");
        lcd.setRGB(colorR, colorG, colorB);
        lcd.setCursor(0, 1);
        out = analogRead(LDR);
        out = (float(float(out)/1000))*100;
        lcd.print(out);
          
        
        }
          
    // print the number of seconds since reset:
    
    delay(1000);
}
