# Order System

Order System låter en kund registrera och följa en order. Systemet kontrollerar produktinformation, lagrar ordern och publicerar en OrderCreated-händelse till ett externt leveranssystem. Betalning verifieras via Payment Gateway.

## Huvudflöde

1. Kunden registrerar en order via webbgränssnittet.
2. Order API tar emot ordern.
3. Order Management sparar ordern i Order Database.
4. Payment Gateway verifierar betalningen.
5. OrderCreated publiceras för Delivery System.

Systemet körs i produktion på en containerplattform. Orderdata ska ägas av Order Management och extern trafik ska använda TLS.
