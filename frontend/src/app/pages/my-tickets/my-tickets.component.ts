// Мои обращения: все обращения в поддержку вошедшего покупателя со статусом и ответом поддержки.
// Django определяет покупателя по токену входа, поэтому чужие обращения и ответы здесь не видны.

import { Component, OnInit, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiService, errorText } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';
import { CustomerTicket } from '../../models';
import { LanguageService } from '../../services/language.service';

@Component({
  selector: 'app-my-tickets',
  imports: [DatePipe, RouterLink],
  template: `<section class="page">
    <header class="page-head">
      <h1>{{ language.tr('My requests') }}</h1>
      <p class="muted">{{ language.tr('Your messages to support and the answers you received.') }}</p>
    </header>

    @if (!auth.user()) {
      <p class="muted"><a routerLink="/login">{{ language.tr('Log in') }}</a> {{ language.tr('to see your requests.') }}</p>
    } @else if (loading()) {
      <p class="muted">{{ language.tr('Loading…') }}</p>
    } @else if (error()) {
      <p class="alert alert-error">{{ language.tr(error()) }}</p>
    } @else {
      @for (t of tickets(); track t.ticket_id) {
        <div class="panel ticket">
          <div class="line">
            <div>
              <strong>{{ language.tr('Request #') }}{{ t.ticket_id }}</strong>
              <p class="muted small">
                {{ topicLabel(t.topic) }} · {{ t.created_at | date: 'dd.MM.yyyy HH:mm':undefined:language.dateLocale() }} ·
                <a [routerLink]="['/orders', t.order_code]">{{ language.tr('Order #') }}{{ t.order_id }}</a>
              </p>
            </div>
            <span class="badge" [class.badge-paid]="t.status === 'closed'" [class.badge-reserved]="t.status !== 'closed'">
              {{ statusLabel(t.status) }}
            </span>
          </div>
          <p>{{ t.message }}</p>
          @if (t.staff_reply) {
            <div class="ticket-reply">
              <strong class="small">{{ language.tr('Support reply') }}</strong>
              <p>{{ t.staff_reply }}</p>
              <p class="muted small">{{ t.replied_at | date: 'dd.MM.yyyy HH:mm':undefined:language.dateLocale() }}</p>
            </div>
          } @else {
            <p class="muted small">{{ language.tr('No reply yet. Support will answer here.') }}</p>
          }
        </div>
      } @empty {
        <div class="empty">
          <p class="muted">{{ language.tr('You have not written to support yet.') }}</p>
          <p class="muted small">{{ language.tr('Open one of your orders and press') }} «{{ language.tr('Contact support about this order') }}».</p>
          <a class="btn" routerLink="/account/orders">{{ language.tr('Go to my orders') }}</a>
        </div>
      }
    }
  </section>`,
})
export class MyTicketsComponent implements OnInit {
  private api = inject(ApiService);
  auth = inject(AuthService);
  language = inject(LanguageService);

  tickets = signal<CustomerTicket[]>([]);
  loading = signal(true);
  error = signal('');

  ngOnInit(): void {
    const token = this.auth.user()?.token;
    if (!token) {
      this.loading.set(false);
      return;
    }
    this.api.getMyTickets(token).subscribe({
      next: (list) => { this.tickets.set(list); this.loading.set(false); },
      error: (err) => { this.error.set(this.language.tr(errorText(err))); this.loading.set(false); },
    });
  }

  statusLabel(status: CustomerTicket['status']): string {
    return this.language.tr(status === 'open' ? 'Open' : status === 'in_progress' ? 'In progress' : 'Closed');
  }

  topicLabel(topic: CustomerTicket['topic']): string {
    return this.language.tr(topic === 'refund' ? 'Refund' : topic === 'delivery' ? 'Delivery' : 'Other');
  }
}
