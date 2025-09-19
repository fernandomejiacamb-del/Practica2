# Practica2: control de motor de DC  por medio de una pagina web y raspberry pico
📌Descripción general:
Este proyecto combina hardware y software para crear un sistema de control de motor de CC simple y eficiente:
El Raspberry Pi Pico ejecuta código en MicroPython, gestiona la conexión WiFi y controla el motor mediante PWM.
El driver L9110S permite el control de velocidad y dirección del motor.
La página móvil, creada con HTML, CSS y JavaScript, ofrece una experiencia visual interactiva con un control deslizante y un medidor gráfico.
El sistema es ideal para practicar conceptos de electrónica básica, programación de microcontroladores y desarrollo web.

## 🏗️ Etapas del Proyecto
1. **Configuración del entorno**  
   Preparar editor de código, instalar Python/MicroPython, flashear la Raspberry Pi Pico o Pico W y realizar las conexiones con el driver L9110S y el motor DC.
2. **Página web móvil**  
   Crear `index.html` con un control deslizante (`range`) y un indicador (Chart.js o `<canvas>`) para visualizar y ajustar en tiempo real la velocidad y sentido del motor.
3. **Programación en MicroPython**  
   Configurar WiFi, montar el servidor web en el Pico y controlar el motor mediante PWM, recibiendo los valores del control deslizante.
4. **Integración y pruebas**  
   Cargar `main.py`, acceder a la IP del Pico desde un navegador y verificar que la velocidad y el sentido del motor se ajustan correctamente.
5. **Documentación y mejoras**  
   Redactar el README y proponer mejoras como reconexión automática de WiFi, modo AP de configuración y autenticación básica.
