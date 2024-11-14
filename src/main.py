import machine
import time
import urandom

# Definition der 8 GPIO-Pins für die LED-Chips
chip_enable_pins = [1, 2, 3, 4, 5, 6, 7, 8]

# Erzeugen eines Arrays von Pin-Objekten im OUTPUT-Modus
chip_enable = [machine.Pin(pin, machine.Pin.OUT, value=1) for pin in chip_enable_pins]

# Definition der Pins für die RGB-Farben (Rot, Grün, Blau)
R_pin = 10
G_pin = 11
B_pin = 12

# Initialisieren der PWM-Ausgänge für die RGB-Pins
R_pwm = machine.PWM(machine.Pin(R_pin))
G_pwm = machine.PWM(machine.Pin(G_pin))
B_pwm = machine.PWM(machine.Pin(B_pin))

# Setzen der PWM-Frequenz für die Farb-LEDs
R_pwm.freq(1000)
G_pwm.freq(1000)
B_pwm.freq(1000)

# Pins für die Wechselschalter-Eingänge
switch_pin_1 = machine.Pin(20, machine.Pin.IN, machine.Pin.PULL_UP)
switch_pin_2 = machine.Pin(21, machine.Pin.IN, machine.Pin.PULL_UP)

# Debounce-Parameter für den Schalter
DEBOUNCE_TIME_MS = 50  # Entprellzeit in Millisekunden

# Definieren einer Klasse für vordefinierte Farben
class Color:
    RED = [1, 0, 0]
    GREEN = [0, 1, 0]
    BLUE = [0, 0, 1]
    YELLOW = [1, 1, 0]
    CYAN = [0, 1, 1]
    MAGENTA = [1, 0, 1]
    WHITE = [1, 1, 1]
    OFF = [0, 0, 0]

# Funktion, um alle LEDs zu deaktivieren
def disable_all():
    for pin in chip_enable:
        pin.value(1)

# Funktion, um eine einzelne LED einzuschalten
def led_on(id, color, brightness=1.0):
    disable_all()
    
    # Berechne die PWM-Duty-Cycles für die RGB-Kanäle
    r = int(color[0] * brightness * 65535)
    g = int(color[1] * brightness * 65535)
    b = int(color[2] * brightness * 65535)

    R_pwm.duty_u16(r)
    G_pwm.duty_u16(g)
    B_pwm.duty_u16(b)

    chip_enable[id].value(0)

# Funktion, um eine zufällige Farbe zu generieren
def get_random_color():
    return [
        urandom.getrandbits(8) / 255,
        urandom.getrandbits(8) / 255,
        urandom.getrandbits(8) / 255
    ]

# Funktion, um eine zufällige LED einzuschalten
def random_led():
    led_index = urandom.getrandbits(3)
    color = get_random_color()
    brightness = urandom.getrandbits(8) / 255
    led_on(led_index, color, brightness)
    time.sleep(urandom.getrandbits(6) / 64)

# Funktion zum Einlesen und Entprellen des Schalters
def read_switch():
    """
    Liest die Stellung des Wechselschalters ein und entprellt ihn.
    Gibt '1' zurück, wenn Stellung 1 aktiv ist, ansonsten '2'.
    """
    # Lesen des Schalterzustands und Entprellen
    state_1 = not switch_pin_1.value()  # LOW bedeutet gedrückt
    state_2 = not switch_pin_2.value()  # LOW bedeutet gedrückt

    # Wenn keine der beiden Positionen stabil ist, warte und prüfe erneut
    start_time = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start_time) < DEBOUNCE_TIME_MS:
        if (not switch_pin_1.value() != state_1) or (not switch_pin_2.value() != state_2):
            state_1 = not switch_pin_1.value()
            state_2 = not switch_pin_2.value()
            start_time = time.ticks_ms()  # Entprellung zurücksetzen

    # Rückgabe der Schalterstellung
    if state_1:
        return 1
    elif state_2:
        return 2
    else:
        return None  # Falls kein stabiler Zustand erkannt wird

g_counter = 1

# Hauptschleife
while True:
    # Einlesen der Schalterstellung
    #switch_position = read_switch()
    switch_position = 2
    
    # Zeige die Schalterstellung auf der Konsole an
    #print(f"Schalterstellung: {switch_position}")
    
    # Zufällige LED-Funktion basierend auf der Schalterstellung
    if switch_position == 1:
        random_led()  # LEDs zufällig blinken lassen
    elif switch_position == 2:
        print('counter:', g_counter, bin(g_counter))
        color = [int(bit) for bit in f"{g_counter:03b}"]
        led_on(g_counter, color)
        g_counter = (g_counter + 1) % 8  # Schiebe den Bit-Counter um 1 nach links
        time.sleep(0.1)  # Kurze Pause, um CPU-Last zu reduzieren
