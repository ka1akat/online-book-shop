// Страница одной книги: информация, средняя оценка, все отзывы и форма своего отзыва.

import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { DatePipe, DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ApiService, errorText } from '../../services/api.service';
import { AccountService } from '../../services/account.service';
import { AuthService } from '../../services/auth.service';
import { CartService } from '../../services/cart.service';
import { Product, Review } from '../../models';
import { StarsComponent } from '../../stars.component';
import { BookTileComponent } from '../../book-tile.component';
import { LanguageService } from '../../services/language.service';
@Component({
  selector: 'app-book',
  imports: [DatePipe, DecimalPipe, FormsModule, RouterLink, StarsComponent, BookTileComponent],
  templateUrl: './book.component.html',
})
export class BookComponent implements OnInit {
  private api = inject(ApiService);
  private route = inject(ActivatedRoute);
  auth = inject(AuthService);
  cart = inject(CartService);
  account = inject(AccountService);
  language = inject(LanguageService);
  productId = '';
  book = signal<Product | null>(null);
  reviews = signal<Review[]>([]);
  loading = signal(true);
  error = signal('');

  // Форма отзыва
  rating = signal(0);        // 0 = ещё не выбрали звёзды
  hoverRating = signal(0);   // подсветка звёзд под мышкой
  comment = '';
  sending = signal(false);
  formError = signal('');
  formDone = signal('');

  // «Notify me»: книги нет на складе — покупатель встаёт в лист ожидания (FR-07)
  notifyEmail = '';
  notifySending = signal(false);
  notifyError = signal('');
  guestNotified = signal(false); // гость оставил email — показываем «мы сообщим»

  // Избранное
  wishlistBusy = signal(false);
  wishlistError = signal('');

  // Уже есть мой отзыв? Тогда форма работает как «изменить отзыв»
  myReview = computed(() => (this.auth.user() ? this.reviews().find((r) => r.is_mine) ?? null : null));

  // «You may also like»: похожие книги из той же категории
  similar = signal<Product[]>([]);

  ngOnInit(): void {
    // Подписка на адрес, а не snapshot: при переходе на похожую книгу (/books/P-1001 -> /books/P-1002)
    // Angular оставляет ту же страницу, и нужно заново загрузить данные новой книги.
    this.route.paramMap.subscribe((params) => {
      this.productId = params.get('id') ?? '';
      this.loading.set(true);
      this.error.set('');
      this.rating.set(0);
      this.comment = '';
      this.guestNotified.set(false);
      this.notifyError.set('');
      this.api.getProduct(this.productId).subscribe({
        next: (book) => { this.book.set(book); this.loading.set(false); },
        error: (err) => { this.error.set(this.language.tr(errorText(err))); this.loading.set(false); },
      });
      this.loadReviews();
      this.api.getSimilar(this.productId).subscribe({ next: (list) => this.similar.set(list), error: () => {} });
      window.scrollTo({ top: 0 });
    });
  }

  loadReviews(): void {
    this.api.getReviews(this.productId, this.auth.user()?.token).subscribe({
      next: (list) => {
        this.reviews.set(list);
        // если отзыв уже есть — заполняем форму им, чтобы было удобно исправить
        const mine = list.find((r) => r.is_mine);
        if (mine && this.rating() === 0) {
          this.rating.set(mine.rating);
          this.comment = mine.comment;
        }
      },
    });
  }

  canAdd(p: Product): boolean {
    return this.cart.quantityOf(p.product_id) < p.available;
  }

  submit(): void {
    const token = this.auth.user()?.token;
    if (!token) {
      // Пользователь вошёл до того, как появились токены: нужно войти заново
      this.formError.set(this.language.tr('Please log out and log in again to leave a review.'));
      return;
    }
    if (this.rating() === 0) {
      this.formError.set(this.language.tr('Choose from 1 to 5 stars.'));
      return;
    }
    this.sending.set(true);
    this.formError.set('');
    this.formDone.set('');
    this.api.addReview(this.productId, this.rating(), this.comment, token).subscribe({
      next: () => {
        this.sending.set(false);
        this.formDone.set(this.language.tr('Thank you! Your review is published.'));
        this.loadReviews();
        // средняя оценка изменилась — берём книгу заново
        this.api.getProduct(this.productId).subscribe({ next: (book) => this.book.set(book) });
      },
      error: (err) => {
        this.formError.set(this.language.tr(errorText(err)));
        this.sending.set(false);
      },
    });
  }

  notifyMe(): void {
    const loggedIn = !!this.auth.user()?.token;
    if (!loggedIn && !this.notifyEmail.trim()) {
      this.notifyError.set(this.language.tr('Enter your e-mail and we will let you know.'));
      return;
    }
    this.notifySending.set(true);
    this.notifyError.set('');
    this.account.notifyMe(this.productId, this.notifyEmail.trim()).subscribe({
      next: () => {
        this.notifySending.set(false);
        if (!loggedIn) this.guestNotified.set(true);
      },
      error: (err) => {
        this.notifySending.set(false);
        this.notifyError.set(this.language.tr(errorText(err)));
      },
    });
  }

  stopWaiting(): void {
    this.notifySending.set(true);
    this.account.stopWaiting(this.productId).subscribe({
      next: () => this.notifySending.set(false),
      error: (err) => {
        this.notifySending.set(false);
        this.notifyError.set(this.language.tr(errorText(err)));
      },
    });
  }

  toggleWishlist(book: Product): void {
    this.wishlistBusy.set(true);
    this.wishlistError.set('');
    this.account.toggleWishlist(book).subscribe({
      next: () => this.wishlistBusy.set(false),
      error: (err) => {
        this.wishlistBusy.set(false);
        this.wishlistError.set(this.language.tr(errorText(err)));
      },
    });
  }
}
