// Страница заказа: таймер брони 15 минут, оплата картой и история попыток оплаты.
// форма обращения в поддержку и ответы поддержки по этому заказу.
import { Component, OnDestroy, OnInit, computed, inject, input, signal } from '@angular/core';
import { DatePipe, DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ApiService, errorText } from '../../services/api.service';
import { CustomerTicket, Order, SupportTicket, SupportTopic } from '../../models';
import { LanguageService } from '../../services/language.service';

@Component({
  selector: 'app-order',
  imports: [DatePipe, DecimalPipe, FormsModule, RouterLink],
  templateUrl: './order.component.html',
})
export class OrderComponent implements OnInit, OnDestroy {
  private api = inject(ApiService);
  language = inject(LanguageService);

  // Секретный код заказа приходит из адреса /orders/:id (включено withComponentInputBinding в app.config.ts).
  // Название параметра осталось id, но внутри теперь длинный случайный код, а не номер заказа.
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

  // Обращения по этому заказу с ответами поддержки
  tickets = signal<CustomerTicket[]>([]);

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
    this.loadTickets();
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
    this.api.getOrder(this.id()).subscribe({
      next: (o) => this.order.set(o),
      error: (err) => this.error.set(this.language.tr(errorText(err))),
    });
  }

  loadTickets(): void {
    this.api.getOrderTickets(this.id()).subscribe({
      next: (list) => this.tickets.set(list),
      error: () => {}, // если не получилось, страница заказа всё равно работает
    });
  }

  statusLabel(status: CustomerTicket['status']): string {
    return this.language.tr(status === 'open' ? 'Open' : status === 'in_progress' ? 'In progress' : 'Closed');
  }

  pay(): void {
    this.paying.set(true);
    this.payError.set('');
    this.api.payOrder(this.id(), this.cardNumber).subscribe({
      next: (o) => {
        this.order.set(o);
        this.paying.set(false);
      },
      error: (err) => {
        this.payError.set(this.language.tr(errorText(err)));
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

  // Кнопка «Send» активна, когда текст не пустой. Email не нужен: заказ определяется секретным кодом
  canSendSupport(): boolean {
    return this.supportMessage.trim().length >= 10 && !this.supportSending();
  }

  sendSupport(): void {
    this.supportSending.set(true);
    this.supportError.set('');
    this.api
      .sendSupportRequest({
        order_code: this.id(),
        topic: this.supportTopic,
        message: this.supportMessage.trim(),
      })
      .subscribe({
        next: (ticket) => {
          this.supportTicket.set(ticket);
          this.supportSending.set(false);
          this.supportMessage = '';
          this.loadTickets(); // новое обращение сразу появляется в списке ниже
        },
        // Если текст не прошёл проверку (грубые слова, ссылки), Django вернёт понятное сообщение.
        // Введённый текст остаётся в форме, его можно поправить и отправить снова.
        error: (err) => {
          this.supportError.set(this.language.tr(errorText(err)));
          this.supportSending.set(false);
        },
      });
  }
}
