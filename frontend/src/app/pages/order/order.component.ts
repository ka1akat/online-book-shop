// Страница заказа: таймер брони 15 минут, оплата картой и история попыток оплаты.

import { Component, OnDestroy, OnInit, computed, inject, input, signal } from '@angular/core';
import { DatePipe, DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ApiService, errorText } from '../../services/api.service';
import { Order } from '../../models';

@Component({
  selector: 'app-order',
  imports: [DatePipe, DecimalPipe, FormsModule, RouterLink],
  templateUrl: './order.component.html',
})
export class OrderComponent implements OnInit, OnDestroy {
  private api = inject(ApiService);

  // id приходит из адреса /orders/:id (включено withComponentInputBinding в app.config.ts)
  id = input.required<string>();

  order = signal<Order | null>(null);
  error = signal('');
  payError = signal('');
  paying = signal(false);
  cardNumber = '';

  private now = signal(Date.now());
  private timer?: ReturnType<typeof setInterval>;

  // Сколько секунд осталось до конца брони
  secondsLeft = computed(() => {
    const o = this.order();
    if (!o) return 0;
    return Math.max(0, Math.floor((new Date(o.reserved_until).getTime() - this.now()) / 1000));
  });

  countdown = computed(() => {
    const s = this.secondsLeft();
    return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
  });

  ngOnInit(): void {
    this.load();
    this.timer = setInterval(() => {
      this.now.set(Date.now());
      const o = this.order();
      // Время вышло — спрашиваем у сервера свежий статус (он станет cancelled)
      if (o?.status === 'reserved' && this.secondsLeft() === 0) this.load();
    }, 1000);
  }

  ngOnDestroy(): void {
    clearInterval(this.timer);
  }

  load(): void {
    this.api.getOrder(Number(this.id())).subscribe({
      next: (o) => this.order.set(o),
      error: (err) => this.error.set(errorText(err)),
    });
  }

  pay(): void {
    this.paying.set(true);
    this.payError.set('');
    this.api.payOrder(Number(this.id()), this.cardNumber).subscribe({
      next: (o) => {
        this.order.set(o);
        this.paying.set(false);
      },
      error: (err) => {
        this.payError.set(errorText(err));
        this.paying.set(false);
        this.load(); // чтобы показать неудачную попытку в истории оплат
      },
    });
  }

  // Красиво группируем цифры карты по 4: 4111 1111 1111 1111
  formatCard(value: string): void {
    const digits = value.replace(/\D/g, '').slice(0, 16);
    this.cardNumber = digits.replace(/(.{4})(?=.)/g, '$1 ');
  }
}
