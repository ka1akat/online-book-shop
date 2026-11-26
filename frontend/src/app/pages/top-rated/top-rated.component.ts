// Top rating: книги с самой высокой средней оценкой покупателей (GET /api/products/top-rated/).

import { Component, OnInit, inject, signal } from '@angular/core';
import { ApiService, errorText } from '../../services/api.service';
import { BookTileComponent } from '../../book-tile.component';
import { Category, Product } from '../../models';

@Component({
  selector: 'app-top-rated',
  imports: [BookTileComponent],
  template: `<section class="page">
    <header class="page-head">
      <h1>Top rating</h1>
      <p class="muted">The best books by our customers' reviews. Only books with at least one review are ranked.</p>
    </header>

    <div class="category-chips">
      <button type="button" class="chip" [class.chip-on]="categoryId() === null" (click)="choose(null)">All</button>
      @for (c of categories(); track c.category_id) {
        <button type="button" class="chip" [class.chip-on]="categoryId() === c.category_id" (click)="choose(c.category_id)">
          {{ c.category_name }}
        </button>
      }
    </div>

    @if (loading()) {
      <p class="muted">Loading…</p>
    } @else if (error()) {
      <p class="alert alert-error">{{ error() }}</p>
    } @else {
      <div class="tile-grid">
        @for (b of books(); track b.product_id; let i = $index) {
          <app-book-tile [book]="b" [rank]="i + 1" />
        } @empty {
          <p class="muted">No reviewed books in this category yet. Leave the first review on a book page!</p>
        }
      </div>
    }
  </section>`,
})
export class TopRatedComponent implements OnInit {
  private api = inject(ApiService);

  books = signal<Product[]>([]);
  categories = signal<Category[]>([]);
  categoryId = signal<number | null>(null);
  loading = signal(true);
  error = signal('');

  ngOnInit(): void {
    this.api.getCategories().subscribe({ next: (list) => this.categories.set(list), error: () => {} });
    this.load();
  }

  choose(categoryId: number | null): void {
    this.categoryId.set(categoryId);
    this.load();
  }

  private load(): void {
    this.loading.set(true);
    this.api.getTopRated(20, this.categoryId()).subscribe({
      next: (list) => { this.books.set(list); this.loading.set(false); },
      error: (err) => { this.error.set(errorText(err)); this.loading.set(false); },
    });
  }
}
