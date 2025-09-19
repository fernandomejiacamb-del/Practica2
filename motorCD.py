# ==========================
# Importación de librerías
# ==========================
import network       # Permite manejar la conexión WiFi en MicroPython
import socket        # Proporciona funciones para crear un servidor web (sockets TCP/IP)
import time          # Librería para pausas y medición de tiempo
from machine import Pin, PWM  # Control de pines GPIO y generación de señal PWM

# ==========================
# Configuración WiFi
# ==========================
SSID = "motoN"          # Nombre de la red WiFi a la que se conectará el microcontrolador
PASSWORD = "12345678"   # Contraseña de la red WiFi

wlan = network.WLAN(network.STA_IF)  # Crea una interfaz de red en modo estación (cliente)
wlan.active(True)                    # Activa la interfaz WiFi
wlan.connect(SSID, PASSWORD)         # Inicia la conexión con la red WiFi

print("Conectando a WiFi...")
while not wlan.isconnected():         # Espera en bucle hasta que la conexión sea exitosa
    time.sleep(1)                     # Pausa de 1 segundo entre cada intento

print("Conectado:", wlan.ifconfig())  # Muestra la información de la conexión (IP, máscara, gateway, DNS)

# ==========================
# Configuración del Motor DC
# ==========================
# El driver L9110S controla el motor a través de dos pines: A-1A y A-1B.
PIN_A = 4   # GPIO para la entrada A-1A del driver
PIN_B = 3   # GPIO para la entrada A-1B del driver

# Inicializa los pines en estado bajo para evitar arranque inesperado del motor
pa_pin = Pin(PIN_A, Pin.OUT, value=0)
pb_pin = Pin(PIN_B, Pin.OUT, value=0)
time.sleep(0.05)  # Pequeña pausa para asegurar la configuración

# Configura los pines en modo PWM (modulación por ancho de pulso)
in1 = PWM(pa_pin)
in2 = PWM(pb_pin)
in1.freq(1000)      # Fija la frecuencia de PWM en 1 kHz
in2.freq(1000)
in1.duty_u16(0)     # Duty cycle inicial 0% (motor apagado)
in2.duty_u16(0)

INVERT = False      # Si se pone en True, invierte el sentido de giro del motor

def set_motor(velocidad):
    """
    Controla la velocidad y dirección del motor DC.
    velocidad: número entero de -100 a 100
      positivo = motor hacia adelante
      negativo = motor en reversa
      0 = motor detenido
    """
    if INVERT:
        velocidad = -velocidad   # Invierte el sentido si está activado

    if velocidad > 0:            # Giro hacia adelante
        duty = int(velocidad * 65535 / 100)  # Conversión de porcentaje a duty cycle (0–65535)
        in1.duty_u16(duty)
        in2.duty_u16(0)
    elif velocidad < 0:          # Giro en reversa
        duty = int(abs(velocidad) * 65535 / 100)
        in1.duty_u16(0)
        in2.duty_u16(duty)
    else:                        # Motor detenido
        in1.duty_u16(0)
        in2.duty_u16(0)

# ==========================
# Página HTML servida por el Pico
# ==========================
# Esta variable contiene todo el código HTML/JS/CSS que se mostrará en el navegador
html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Control Motor DC</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
    body {
      background-image: url(https://www.sekinamayu.com/wp-content/uploads/2023/12/Sousou-no-Frieren-Anime-Blog-Banner.jpg);
      background-repeat: no-repeat; background-size: cover; background-position: center; background-attachment: fixed; font-family: Arial, sans-serif; text-align: center;
    }
    p {
      color: #C908C1;
    }
    h2{
      color: #C908C1;
    }
    </style>
</head>
<body class="bg-dark text-light text-center">
    <div class="container py-4">
        <h1 class="mb-4">Control de Motor DC</h1>
        <label for="velocidad" class="form-label">Velocidad del Motor (%)</label>
        <!-- Control deslizante para ajustar velocidad -->
        <input type="range" class="form-range" min="-100" max="100" value="0" id="velocidad">
        <p class="mt-3">Velocidad actual: <span id="valor">0</span>%</p>
        <!-- Indicador circular de velocidad -->
        <canvas id="indicador" width="200" height="200"></canvas>
    </div>
<script>
const slider = document.getElementById("velocidad");    // Elemento del slider
const valor = document.getElementById("valor");         // Span que muestra el valor
const ctx = document.getElementById("indicador").getContext("2d"); // Contexto de dibujo

// Configuración del gráfico tipo 'doughnut' (semicírculo)
let chart = new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: ["Velocidad", "Restante"],
        datasets: [{
            data: [0, 100],
            backgroundColor: ["#0d6efd", "#343a40"],
            borderWidth: 1
        }]
    },
    options: {
        circumference: 180,
        rotation: 270,
        cutout: "70%",
        plugins: {legend: {display: false}}
    }
});

// Evento que se dispara al mover el slider
slider.addEventListener("input", () => {
    let val = parseInt(slider.value);    // Lee el valor del slider
    valor.textContent = val;              // Actualiza el texto visible
    fetch(`/set?valor=${val}`);           // Envía el valor al servidor
    chart.data.datasets[0].data[0] = Math.abs(val);    // Actualiza el gráfico
    chart.data.datasets[0].data[1] = 100 - Math.abs(val);
    chart.update();
});
</script>
</body>
</html>
"""

# ==========================
# Servidor Web en el Pico
# ==========================
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]  # Dirección IP y puerto (0.0.0.0:80)
s = socket.socket()                               # Crea un socket TCP
s.bind(addr)                                      # Lo asocia a la dirección y puerto
s.listen(1)                                       # Permite una conexión a la vez
print("Servidor corriendo en http://", wlan.ifconfig()[0])

while True:
    cl, addr = s.accept()                         # Espera una nueva conexión de cliente
    print("Cliente conectado:", addr)
    request = cl.recv(1024).decode()               # Recibe la solicitud HTTP

    # Si la solicitud contiene un valor de velocidad, lo procesa
    if "/set?valor=" in request:
        try:
            val_str = request.split("/set?valor=")[1].split(" ")[0]  # Extrae el número
            val = int(val_str)
            print("Velocidad recibida:", val)
            set_motor(val)                         # Ajusta el motor con el nuevo valor
        except:
            pass                                    # Ignora errores de conversión

    # Envía la página HTML como respuesta
    cl.send("HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n")
    cl.send(html)
    cl.close()                                     # Cierra la conexión con el cliente
