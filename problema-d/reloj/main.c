/*
 * Laboratorio 5 - Problema D, Actividad 5
 * Consumo frente a la frecuencia de reloj (registro CLKPR)
 *
 * El programa divide el reloj del sistema con CLKPR y despues hace lo mismo
 * que haria a 16 MHz, SIN corregir nada:
 *   - Timer0 configurado para 1 ms (pensando en 16 MHz).
 *   - LED que cambia cada 200 "ms" contados con ese Timer0.
 *   - UART configurada para 9600 baud (pensando en 16 MHz) que manda una 'U'.
 *
 * Asi se ve que al dividir el reloj tambien se dividen los timers y la UART:
 *   - el LED cambia cada 200 ms x DIVISOR,
 *   - la UART sale a 9600 / DIVISOR baud (el monitor a 9600 muestra basura).
 *
 * Mientras tanto se mide el consumo en estado activo para cada divisor.
 *
 * Conexiones (Arduino UNO):
 *   D13 LED -> osciloscopio, para medir el tiempo entre cambios
 *   D1 (TX) -> monitor serie
 */

#define F_CPU 16000000UL

#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/wdt.h>
#include <stdint.h>

/* Valores de CLKPS para CLKPR (hoja de datos, tabla "Clock Prescaler Select") */
#define DIV_1    0     /* 16 MHz  */
#define DIV_2    1     /*  8 MHz  */
#define DIV_8    3     /*  2 MHz  */
#define DIV_64   6     /* 250 kHz */
#define DIV_128  7     /* 125 kHz */

/* ---- Elegir aca el divisor a probar ---- */
#define DIVISOR  DIV_1

#define LED PB5

volatile uint32_t ms = 0;


ISR(TIMER0_COMPA_vect)
{
	ms++;
}


int main(void)
{
	uint32_t ultimo = 0;
	uint32_t ahora;

	MCUSR = 0;
	wdt_disable();

	/* Cambio del prescaler del reloj: primero se escribe solo CLKPCE y, antes
	   de 4 ciclos, el valor nuevo. Se hace con las interrupciones apagadas. */
	cli();
	CLKPR = (1 << CLKPCE);
	CLKPR = DIVISOR;

	DDRB |= (1 << LED);

	/* Timer0: 1 ms si el reloj fuera de 16 MHz */
	TCCR0A = (1 << WGM01);
	TCCR0B = (1 << CS01) | (1 << CS00);
	OCR0A = 249;
	TIMSK0 = (1 << OCIE0A);

	/* UART: 9600 baud si el reloj fuera de 16 MHz */
	UBRR0 = 103;
	UCSR0B = (1 << TXEN0);
	UCSR0C = (1 << UCSZ01) | (1 << UCSZ00);

	sei();

	while (1)
	{
		cli();
		ahora = ms;
		sei();

		if ((uint32_t)(ahora - ultimo) >= 200)
		{
			ultimo += 200;

			PORTB ^= (1 << LED);

			if (UCSR0A & (1 << UDRE0))
				UDR0 = 'U';
		}
	}
}
