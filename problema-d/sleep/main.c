/*
 * Laboratorio 5 - Problemas C y D
 * Banco de pruebas de los modos Sleep
 *
 * Sirve para tres mediciones:
 *   - Consumo en cada modo Sleep (Problema D, Actividad 1): el micro queda
 *     dormido en el modo elegido hasta que se aprieta el pulsador.
 *   - Efecto de cada periferico (Problema D, Actividad 2): con PRR_MASCARA se
 *     apagan perifericos de a uno y se mide la diferencia.
 *   - Tiempo de despertar (Problema D, Actividad 3): se mide con el
 *     osciloscopio el tiempo entre el flanco del pulsador (canal 1, D2) y el
 *     flanco del pin de prueba (canal 2, D12).
 *
 * Conexiones (Arduino UNO):
 *   D2  pulsador a GND (evento de despertar)   -> canal 1 del osciloscopio
 *   D12 pin de prueba                          -> canal 2 del osciloscopio
 *   D13 LED: queda prendido 1 s despues de cada despertar
 *
 * Fuente de despertar: interrupcion por cambio de pin en D2 (PCINT18).
 * Segun la hoja de datos, el cambio de pin se detecta sin reloj, asi que
 * despierta al micro en todos los modos (Idle, ADC Noise Reduction y
 * Power-Down). Ademas, a diferencia de INT0 por nivel, se puede simular en
 * PICSimLab.
 */

#define F_CPU 16000000UL

#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/sleep.h>
#include <avr/wdt.h>
#include <util/delay.h>
#include <stdint.h>

/* ---- Elegir aca el modo a probar ---- */
#define SIN_DORMIR      0     /* el micro queda despierto esperando (referencia) */
#define MODO_IDLE       1
#define MODO_ADC_NR     2     /* ADC Noise Reduction */
#define MODO_POWER_DOWN 3

#define MODO            MODO_POWER_DOWN

/* ---- Perifericos apagados con PRR (un 1 apaga) ----
   ADC 0x01 | USART0 0x02 | SPI 0x04 | Timer1 0x08 | Timer0 0x20 | Timer2 0x40 | TWI 0x80
   Ejemplos:  0x00 = todos prendidos      0x01 = solo el ADC apagado
              0xEF = todos apagados (el bit 4 es reservado y no se toca) */
#define PRR_MASCARA     0x00

#define LED PB5
#define PRUEBA PB4
#define BUTTON PD2


ISR(PCINT2_vect)
{
	PORTB |= (1 << PRUEBA);       /* primera accion observable despues de despertar */
	PCMSK2 &= ~(1 << PCINT18);    /* se apaga hasta que suelten el boton */
}


int main(void)
{
	MCUSR = 0;
	wdt_disable();

	DDRB |= (1 << LED) | (1 << PRUEBA);
	PORTB &= ~((1 << LED) | (1 << PRUEBA));

	DDRD &= ~(1 << BUTTON);
	PORTD |= (1 << BUTTON);

	ADCSRA &= ~(1 << ADEN);       /* ADC deshabilitado antes de tocar PRR */
	PRR = PRR_MASCARA;

	PCICR = (1 << PCIE2);         /* habilita el grupo de cambio de pin del puerto D */

	sei();

	while (1)
	{
		/* Espera a que suelten el boton (programa de prueba: aca se puede esperar) */
		while (!(PIND & (1 << BUTTON)));
		_delay_ms(50);

		PORTB &= ~(1 << PRUEBA);
		PCIFR = (1 << PCIF2);         /* borra una bandera vieja */
		PCMSK2 = (1 << PCINT18);      /* solo D2 */

#if MODO == SIN_DORMIR
		while (!(PORTB & (1 << PRUEBA)));        /* despierto, esperando el boton */
#else
#if MODO == MODO_IDLE
		set_sleep_mode(SLEEP_MODE_IDLE);
#elif MODO == MODO_ADC_NR
		set_sleep_mode(SLEEP_MODE_ADC);
#else
		set_sleep_mode(SLEEP_MODE_PWR_DOWN);
#endif
		sleep_enable();
		sleep_cpu();              /* <- aca se mide el consumo del modo */
		sleep_disable();
#endif

		/* Desperto: lo muestra 1 s en el LED y vuelve a dormir */
		PORTB |= (1 << LED);
		_delay_ms(1000);
		PORTB &= ~(1 << LED);
	}
}
