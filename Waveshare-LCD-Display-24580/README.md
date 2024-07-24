Waveshare-LCD-Display-24580

Rundes 1.28-Zoll-IPS-LCD-Touch Display - Waveshare 24580 
(Anleitung für CircuitPython)

Wenn man den RP 2040 mit CircuitPython als Firmware nutzen will, muss man (fast) alles selbst entwickeln, denn im Netz ist dazu z.Z. nichts zu finden. Ich gehe deshalb zuerst darauf ein, wie man das Display in Betrieb nimmt und die Touchfunktionalität testet. Als erstes wird das Board mit der Firmware CircuitPython 9.0.5 geflasht. Eine ausführliche Beschreibung dazu finden Sie hier unter dem Arbeitsschritt 'Installation von CircuitPython' bei https://www.dgebhardt.de/pico-lcd-1.28-rund/download_pico_watch.html.

Danach kopieren Sie die erforderlichen Bibliotheken in den 'lib'-Ordner. Das sind:

    cst816.py (Treiber für den Touch-Sensor)
    gc9a01.py (Treiber für das Display)
    adafruit_display_shapes (Ordner mit Treibern für grafische Elemente)
    adafruit_display_text (Ordner mit Treibern für Textlabels)
    adafruit_ticks.mpy (Treiber für Zeitmessungen)

Probieren Sie die Beispiele aus und lesen auch die Erläuterungen auf meiner Website
https://www.dgebhardt.de/pico-lcd-1.28-rund/touch_display.html .
