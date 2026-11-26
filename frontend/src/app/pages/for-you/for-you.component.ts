// «For you» в личном кабинете: покупатель отмечает любимые категории и получает подборку книг.

import { Component, OnInit, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ApiService, errorText } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';
import { BookTileComponent } from '../../book-tile.component';
import { Category, Recommendations } from '../../models';
import { LanguageService } from '../../services/language.service';

@Component({
  selector: 'app-for-you',
  imports: [BookTileComponent, RouterLink],
  template: `<section>
    <header class="page-head">
      <h1>{{ language.tr('For you') }}</h1>
      <p class="muted">{{ language.tr('Choose the categories you like, and we will pick books for you.') }}</p>
    </header>

    <div class="panel prefs">
      <strong>{{ language.tr('My favourite categories') }}</strong>
      <div class="category-chips">
        @for (c of categories(); track c.category_id) {
          <button type="button" class="chip" [class.chip-on]="chosen().has(c.category_id)"
            [attr.aria-pressed]="chosen().has(c.category_id)" (click)="toggle(c.category_id)">
            {{ chosen().has(c.category_id) ? '✓ ' : '' }}{{ language.category(c.category_name) }}
          </button>
        }
      </div>
      <div class="prefs-actions">
        <button class="btn" type="button" [disabled]="saving() || !changed()" (click)="save()">
          {{ language.tr(saving() ? 'Saving…' : 'Save') }}
        </button>
        @if (saved()) { <span class="muted small">{{ language.tr('Saved ✓') }}</span> }
        @if (error()) { <span class="alert alert-error">{{ language.tr(error()) }}</span> }
      </div>
    </div>

    @if (recs(); as r) {
      <h2>{{ language.tr('Recommended for you') }}</h2>
      <p class="muted small">
        @switch (r.based_on) {
          @case ('favorites') { {{ language.tr('Recommended from your favourite categories:') }} {{ language.categoryList(r.categories) }}. }
          @case ('activity') { {{ language.tr('Based on your wishlist, orders and reviews:') }} {{ language.categoryList(r.categories) }}. }
          @case ('top_rated') { {{ language.tr('You have not chosen categories yet, so here are our best-rated books.') }} }
        }
      </p>
      <div class="tile-grid">
        @for (b of r.books; track b.product_id) {
          <app-book-tile [book]="b" />
        } @empty {
          <p class="muted">{{ language.tr('You already have all books from these categories. Look at the top rated books in the') }} <a routerLink="/catalog">{{ language.tr('catalog') }}</a>.</p>
        }
      </div>
    }
  </section>`,
})
export class ForYouComponent implements OnInit {
  private api = inject(ApiService);
  private auth = inject(AuthService);
  language = inject(LanguageService);

  categories = signal<Category[]>([]);
  chosen = signal(new Set<number>());
  private savedIds = signal(new Set<number>());
  recs = signal<Recommendations | null>(null);
  saving = signal(false);
  saved = signal(false);
  error = signal('');

  private get token(): string {
    return this.auth.user()?.token ?? '';
  }

  ngOnInit(): void {
    this.api.getCategories().subscribe({ next: (list) => this.categories.set(list), error: () => {} });
    this.api.getPreferences(this.token).subscribe({
      next: (p) => { this.chosen.set(new Set(p.category_ids)); this.savedIds.set(new Set(p.category_ids)); },
      error: () => {},
    });
    this.loadRecommendations();
  }

  toggle(id: number): void {
    const next = new Set(this.chosen());
    if (next.has(id)) next.delete(id); else next.add(id);
    this.chosen.set(next);
    this.saved.set(false);
  }

  changed(): boolean {
    const a = this.chosen(), b = this.savedIds();
    return a.size !== b.size || [...a].some((id) => !b.has(id));
  }

  save(): void {
    this.saving.set(true);
    this.error.set('');
    this.api.savePreferences([...this.chosen()], this.token).subscribe({
      next: (p) => {
        this.savedIds.set(new Set(p.category_ids));
        this.saving.set(false);
        this.saved.set(true);
        this.loadRecommendations();
      },
      error: (err) => { this.saving.set(false); this.error.set(this.language.tr(errorText(err))); },
    });
  }

  private loadRecommendations(): void {
    this.api.getRecommendations(this.token).subscribe({ next: (r) => this.recs.set(r), error: () => {} });
  }
}
