// AccountService — личные списки покупателя, который вошёл: лист ожидания (уведомления) и избранное.
// Их нужно знать сразу на нескольких страницах (счётчик в меню, кнопки на странице книги),
// поэтому они хранятся здесь, а не в одном компоненте.

import { Injectable, computed, effect, inject, signal } from '@angular/core';
import { Observable, tap } from 'rxjs';
import { Product, StockRequestNotice } from '../models';
import { ApiService } from './api.service';
import { AuthService } from './auth.service';

@Injectable({ providedIn: 'root' })
export class AccountService {
  private api = inject(ApiService);
  private auth = inject(AuthService);

  notifications = signal<StockRequestNotice[]>([]);
  wishlist = signal<Product[]>([]);

  // Книги вернулись, а покупатель ещё не открыл уведомления — число в меню
  unreadCount = computed(() => this.notifications().filter((n) => n.notified && !n.is_read).length);
  private wishlistIds = computed(() => new Set(this.wishlist().map((p) => p.product_id)));

  constructor() {
    // Вошёл — загружаем списки; вышел — очищаем, чтобы следующий человек не увидел чужое
    effect(() => {
      if (this.auth.user()?.token) {
        this.refresh();
      } else {
        this.notifications.set([]);
        this.wishlist.set([]);
      }
    });
  }

  refresh(): void {
    const token = this.auth.user()?.token;
    if (!token) return;
    this.api.getNotifications(token).subscribe({ next: (list) => this.notifications.set(list), error: () => {} });
    this.api.getWishlist(token).subscribe({ next: (list) => this.wishlist.set(list), error: () => {} });
  }

  // ---------- Лист ожидания ----------

  waitingFor(productId: string): StockRequestNotice | null {
    return this.notifications().find((n) => n.product_id === productId) ?? null;
  }

  notifyMe(productId: string, email = ''): Observable<StockRequestNotice> {
    return this.api.notifyMe(productId, email, this.auth.user()?.token).pipe(
      tap((notice) => {
        if (!this.auth.user()?.token) return; // гостю список не показываем
        this.notifications.update((list) => [notice, ...list.filter((n) => n.product_id !== productId)]);
      }),
    );
  }

  stopWaiting(productId: string): Observable<void> {
    return this.api.stopWaiting(productId, this.auth.user()?.token ?? '').pipe(
      tap(() => this.notifications.update((list) => list.filter((n) => n.product_id !== productId))),
    );
  }

  markAllRead(): void {
    const token = this.auth.user()?.token;
    if (!token || this.unreadCount() === 0) return;
    this.api.markNotificationsRead(token).subscribe({
      next: () => this.notifications.update((list) => list.map((n) => (n.notified ? { ...n, is_read: true } : n))),
      error: () => {},
    });
  }

  // ---------- Избранное ----------

  inWishlist(productId: string): boolean {
    return this.wishlistIds().has(productId);
  }

  toggleWishlist(product: Product): Observable<unknown> {
    const token = this.auth.user()?.token ?? '';
    if (this.inWishlist(product.product_id)) {
      return this.api.removeFromWishlist(product.product_id, token).pipe(
        tap(() => this.wishlist.update((list) => list.filter((p) => p.product_id !== product.product_id))),
      );
    }
    return this.api.addToWishlist(product.product_id, token).pipe(
      tap(() => this.wishlist.update((list) => [product, ...list])),
    );
  }
}
