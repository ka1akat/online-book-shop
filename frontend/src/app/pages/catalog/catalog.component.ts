import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { DecimalPipe, NgTemplateOutlet } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { ApiService, errorText } from '../../services/api.service';
import { CartService } from '../../services/cart.service';
import { Category, Product, ProductFilters } from '../../models';
import { StarsComponent } from '../../stars.component';

@Component({
  selector: 'app-catalog',
  imports: [DecimalPipe, FormsModule, NgTemplateOutlet, RouterLink, StarsComponent],
  templateUrl: './catalog.component.html',
})
export class CatalogComponent implements OnInit {
  private api = inject(ApiService);
  cart = inject(CartService);
  auth = inject(AuthService);

  products = signal<Product[]>([]);
  loading = signal(true);
  error = signal('');

  categories = signal<Category[]>([]);

  // Top rating: 3 лучшие книги по средней оценке (GET /api/products/top-rated/?limit=3)
  podium = signal<Product[]>([]);
  // Порядок на подиуме слева направо: #2, #1, #3 — первое место в центре и выше
  podiumOrder = computed(() => {
    const [first, second, third] = this.podium();
    return [
      second && { rank: 2, book: second },
      first && { rank: 1, book: first },
      third && { rank: 3, book: third },
    ].filter((place): place is { rank: number; book: Product } => !!place);
  });

  // Все фильтры в одном объекте. Каждый раз, когда что-то меняется,
  // отправляем их в Django, и база возвращает уже отфильтрованный список.
  filters: ProductFilters = {
    category_id: null,
    min_price: null,
    max_price: null,
    min_rating: null,
    ordering: '',
  };

  // Цвет «обложки» зависит от жанра — просто для красоты
  private palette = ['#2f5d50', '#8a3b2e', '#3b4a7a', '#6b4f2a', '#5a3d6e', '#2d6170'];

  ngOnInit(): void {
    this.api.getCategories().subscribe({ next: (items) => this.categories.set(items) });
    this.load();
    this.loadPodium();
  }

  loadPodium(): void {
    this.api.getTopRated(3, this.filters.category_id).subscribe({
      next: (list) => this.podium.set(list),
      error: () => this.podium.set([]),
    });
  }

  load(): void {
    this.loading.set(true);
    this.error.set('');
    this.api.getProducts(this.filters).subscribe({
      next: (list) => { this.products.set(list); this.loading.set(false); },
      error: (err) => { this.error.set(errorText(err)); this.loading.set(false); },
    });
  }

  selectCategory(categoryId: number | null): void {
    this.filters.category_id = categoryId;
    this.load();
    this.loadPodium(); // подиум показывает лучших в выбранной категории
  }

  resetFilters(): void {
    this.filters = { ...this.filters, min_price: null, max_price: null, min_rating: null, ordering: '' };
    this.load();
  }

  hasExtraFilters(): boolean {
    const f = this.filters;
    return f.min_price !== null || f.max_price !== null || f.min_rating !== null || f.ordering !== '';
  }

  coverColor(p: Product): string {
    const n = [...p.product_id].reduce((s, ch) => s * 31 + ch.charCodeAt(0), 7);
    return this.palette[n % this.palette.length];
  }

  canAdd(p: Product): boolean {
    return this.cart.quantityOf(p.product_id) < p.available;
  }
}
