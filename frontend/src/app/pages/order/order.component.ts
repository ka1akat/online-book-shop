// Страница заказа: таймер брони 15 минут, оплата картой и история попыток оплаты.
// и форма обращения в поддержку.
import { Component, OnDestroy, OnInit, computed, inject, input, signal } from '@angular/core';
import { DatePipe, DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ApiService, errorText } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';
import { Order, SupportTicket, SupportTopic } from '../../models';

@Component({
  selector: 'app-order',
  imports: [DatePipe, DecimalPipe, FormsModule, RouterLink],
  templateUrl: './order.component.html',
})
export class OrderComponent implements OnInit, OnDestroy {
  private api = inject(ApiService);

  private auth = inject(AuthService);
  user = this.auth.user; // кто вошёл на сайт (или null)

  // id приходит из адреса /orders/:id (включено withComponentInputBinding в app.config.ts)
  id = input.required<string>();

  order = signal<Order | null>(null);
  error = signal('');
  payError = signal('');
  paying = signal(false);
  cardNumber = '';

  // Форма обращения в поддержку
  supportOpen = signal(false);
  supportSending = signal(false);
  supportError = signal('');
  supportTicket = signal<SupportTicket | null>(null); // не null, когда обращение уже отправлено
  supportTopic: SupportTopic = 'refund';
  supportMessage = '';
  supportEmail = '';

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

  toggleSupport(): void {
    this.supportOpen.update((open) => !open);
    this.supportError.set('');
  }

  // Кнопка «Send» активна, когда есть кому ответить (email или вход) и текст не пустой
  canSendSupport(): boolean {
    const knowsCustomer = !!this.auth.user() || this.supportEmail.includes('@');
    return knowsCustomer && this.supportMessage.trim().length >= 5 && !this.supportSending();
  }

  sendSupport(): void {
    this.supportSending.set(true);
    this.supportError.set('');
    const user = this.auth.user();
    this.api
      .sendSupportRequest(
        {
          order_id: Number(this.id()),
          topic: this.supportTopic,
          message: this.supportMessage.trim(),
          // Вошедшего покупателя Django узнаёт по токену, email не нужен
          email: user ? undefined : this.supportEmail.trim(),
        },
        user?.token,
      )
      .subscribe({
        next: (ticket) => {
          this.supportTicket.set(ticket);
          this.supportSending.set(false);
          this.supportMessage = '';
        },
        error: (err) => {
          this.supportError.set(errorText(err));
          this.supportSending.set(false);
        },
      });
  }
}
