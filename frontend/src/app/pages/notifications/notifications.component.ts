// Уведомления и мой лист ожидания: какие книги я жду и какие уже вернулись на склад (FR-07).

import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AccountService } from '../../services/account.service';
import { ApiService } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';
import { LanguageService } from '../../services/language.service';

@Component({
  selector: 'app-notifications',
  imports: [DatePipe, RouterLink],
  template: `<section class="page">
    <header class="page-head">
      <h1>{{ language.tr('Notifications') }}</h1>
      <p class="muted">{{ language.tr('Books you are waiting for. When a book is back in stock, it appears at the top.') }}</p>
    </header>

    @if (!auth.user()) {
      <p class="muted"><a routerLink="/login">{{ language.tr('Log in') }}</a> {{ language.tr('to see your notifications and waiting list.') }}</p>
    } @else {
      @if (backInStock().length > 0) {
        <h2>{{ language.tr('Back in stock') }}</h2>
        @for (n of backInStock(); track n.request_id) {
          <article class="notice" [class.notice-new]="newIds().has(n.request_id)">
            <div>
              @if (newIds().has(n.request_id)) { <span class="badge badge-paid">{{ language.tr('New') }}</span> }
              <strong>{{ language.bookTitle(n.product_name) }}</strong>&nbsp;<span class="muted">{{ language.tr('Author:') }} {{ language.authorName(n.author) }}</span>
              <p class="muted small">
                {{ language.tr(n.in_stock ? 'Back in stock' : 'Was back, but sold out again') }}
                · {{ n.notified_at | date: 'd MMM y, HH:mm':undefined:language.dateLocale() }}
              </p>
            </div>
            <a class="btn" [routerLink]="['/books', n.product_id]">{{ language.tr(n.in_stock ? 'Buy now' : 'Open') }}</a>
          </article>
        }
      }

      <h2>{{ language.tr('Waiting list') }}</h2>
      @for (n of waiting(); track n.request_id) {
        <article class="notice">
          <div>
            <strong>{{ language.bookTitle(n.product_name) }}</strong>&nbsp;<span class="muted">{{ language.tr('Author:') }} {{ language.authorName(n.author) }}</span>
            <p class="muted small">{{ language.tr('Waiting since') }} {{ n.requested_at | date: 'd MMM y':undefined:language.dateLocale() }}</p>
          </div>
          <button type="button" class="btn btn-secondary" (click)="account.stopWaiting(n.product_id).subscribe()">
          {{ language.tr('Stop waiting') }}
          </button>
        </article>
      } @empty {
        <p class="muted">
          {{ language.tr('You are not waiting for any book. Press “Notify me” on a sold-out book in the') }}
          <a routerLink="/catalog">{{ language.tr('catalog') }}</a>.
        </p>
      }
    }
  </section>`,
})
export class NotificationsComponent implements OnInit {
  private api = inject(ApiService);
  auth = inject(AuthService);
  account = inject(AccountService);
  language = inject(LanguageService);

  // Какие уведомления были новыми в момент открытия страницы: метка «New» держится до следующего захода
  newIds = signal(new Set<number>());

  backInStock = computed(() => this.account.notifications().filter((n) => n.notified));
  waiting = computed(() => this.account.notifications().filter((n) => !n.notified));

  ngOnInit(): void {
    const token = this.auth.user()?.token;
    if (!token) return;
    this.api.getNotifications(token).subscribe({
      next: (list) => {
        this.account.notifications.set(list);
        this.newIds.set(new Set(list.filter((n) => n.notified && !n.is_read).map((n) => n.request_id)));
        // Страницу открыли — уведомления прочитаны, счётчик в меню обнуляется
        this.account.markAllRead();
      },
    });
  }
}
