/**
 * This turns the ESP32S3 mini into a Bluetooth LE keyboard that writes passwords
 * Author : KTB
 * Version: V1.0
 * Date   : 2025/11/02
 */
#include <Adafruit_NeoPixel.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>

#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"
#define RGB_PIN 21 // Onboard RGB LED pin
#define NUM_PIXELS 1 // Only one LED
const int buttonPin = 4;  // the number of the pushbutton pin
int buttonState = 0;  // variable for reading the pushbutton status

Adafruit_NeoPixel pixel(NUM_PIXELS, RGB_PIN, NEO_GRB + NEO_KHZ800);
void setup() {
  // initialize the pushbutton pin as an input:
  pinMode(buttonPin, INPUT_PULLUP);
  pixel.begin();
  pixel.setBrightness(100); // Adjust brightness (0-255)
  Serial.begin(115200);
  Serial.println("Starting Gate Remote work!");
  BLEDevice::init("AFLGateOpen");
  BLEServer *pServer = BLEDevice::createServer();
  BLEService *pService = pServer->createService(SERVICE_UUID);
  BLECharacteristic *pCharacteristic = pService->createCharacteristic(
                                         CHARACTERISTIC_UUID,
                                         BLECharacteristic::PROPERTY_READ |
                                         BLECharacteristic::PROPERTY_WRITE
                                       );

  pCharacteristic->setValue("Hello World says Neil");
  pService->start();
  // BLEAdvertising *pAdvertising = pServer->getAdvertising();  // this still is working for backward compatibility
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  pAdvertising->setMinPreferred(0x06);  // functions that help with iPhone connections issue
  pAdvertising->setMinPreferred(0x12);
  BLEDevice::startAdvertising();
  Serial.println("Characteristic defined! Now you can read it in your phone!");
}

void loop() {
  // read the state of the pushbutton value:
  buttonState = digitalRead(buttonPin);
  // check if the pushbutton is pressed. If it is, the buttonState is LOW:
  if (buttonState == LOW) {
    Serial.println("gateopen");
    pixel.setPixelColor(0, pixel.Color(0, 255, 0));
    pixel.show();
    delay(1000);
    pixel.setPixelColor(0, pixel.Color(0, 0, 0));
    pixel.show();
    delay(500);
    Serial.println("triggred");

  }
  
  delay(250);
}
