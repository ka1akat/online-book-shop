import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { DecimalPipe, NgTemplateOutlet } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { ApiService, errorText } from '../../services/api.service';
import { CartService } from '../../services/cart.service';
import { Category, Product, ProductFilters } from '../../models';
import { StarsComponent } from '../../stars.component';
import { LanguageService } from '../../services/language.service';

// Текст -> слова для поиска: нижний регистр, ё = е, всё кроме букв и цифр — разделитель
function words(text: string): string[] {
  return text.toLocaleLowerCase().replace(/ё/g, 'е').split(/[^\p{L}\p{N}]+/u).filter(Boolean);
}

// Каждое слово запроса должно быть началом какого-то слова в тексте:
// «дост» находит «Достоевский», но «кинг» не находит «Хокинг»
function matches(text: string, query: string[]): boolean {
  const textWords = words(text);
  return query.every((q) => textWords.some((w) => w.startsWith(q)));
}

@Component({
  selector: 'app-catalog',
  imports: [DecimalPipe, FormsModule, NgTemplateOutlet, RouterLink, StarsComponent],
  templateUrl: './catalog.component.html',
  host: { '(document:click)': 'closeSuggestionsOnOutsideClick($event)' },
})
export class CatalogComponent implements OnInit {
  private api = inject(ApiService);
  cart = inject(CartService);
  auth = inject(AuthService);
  language = inject(LanguageService);

  products = signal<Product[]>([]);
  searchQuery = signal('');
  searchOpen = signal(false);
  selectedAuthor = signal('');
  selectedProductId = signal('');
  // Слова запроса: «Гарри поттер» -> ['гарри', 'поттер'] (без регистра, ё = е, без знаков препинания)
  private queryWords = computed(() => words(this.searchQuery()));

  authorSuggestions = computed(() => {
    const query = this.queryWords();
    if (!query.length) return [];
    const uniqueAuthors = new Map<string, string>();
    for (const product of this.products()) {
      const label = this.language.authorName(product.author);
      if (matches(`${label} ${product.author}`, query)) uniqueAuthors.set(product.author, label);
    }
    return [...uniqueAuthors].map(([value, label]) => ({ value, label }));
  });
  bookSuggestions = computed(() => {
    const query = this.queryWords();
    if (!query.length) return [];
    return this.products()
      .filter((product) => matches(`${this.language.bookTitle(product.product_name)} ${product.product_name}`, query))
      .slice(0, 6);
  });
  visibleProducts = computed(() => {
    const query = this.queryWords();
    const productId = this.selectedProductId();
    const author = this.selectedAuthor();
    if (productId) return this.products().filter((product) => product.product_id === productId);
    if (author) return this.products().filter((product) => product.author === author);
    if (!query.length) return this.products();
    return this.products().filter((product) => matches([
      product.product_name,
      product.author,
      this.language.bookTitle(product.product_name),
      this.language.authorName(product.author),
    ].join(' '), query));
  });
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
      error: (err) => { this.error.set(this.language.tr(errorText(err))); this.loading.set(false); },
    });
  }

  selectCategory(categoryId: number | null): void {
    // Новая категория — новый просмотр: старый поиск и выбранная книга/автор сбрасываются,
    // иначе можно получить пустой список (книга из подсказок не входит в эту категорию)
    this.clearSearch();
    this.setCategory(categoryId);
  }

  private setCategory(categoryId: number | null): void {
    if (this.filters.category_id === categoryId) return;
    this.filters.category_id = categoryId;
    this.load();
    this.loadPodium(); // подиум показывает лучших в выбранной категории
  }

  updateSearch(value: string): void {
    this.searchQuery.set(value);
    this.selectedAuthor.set('');
    this.selectedProductId.set('');
    this.searchOpen.set(true);
    // Поиск идёт по всему каталогу, а не только по выбранной категории
    if (value.trim()) this.setCategory(null);
  }

  private clearSearch(): void {
    this.searchQuery.set('');
    this.selectedAuthor.set('');
    this.selectedProductId.set('');
    this.searchOpen.set(false);
  }

  closeSuggestions(): void {
    this.searchOpen.set(false);
  }

  // Клик мимо поля поиска и списка подсказок закрывает список
  closeSuggestionsOnOutsideClick(event: MouseEvent): void {
    const target = event.target as HTMLElement | null;
    if (!target?.closest('.catalog-search-wrap')) this.searchOpen.set(false);
  }

  chooseAuthor(author: string): void {
    this.selectedAuthor.set(author);
    this.selectedProductId.set('');
    this.searchQuery.set(this.language.authorName(author));
    this.searchOpen.set(false);
    this.setCategory(null);
  }

  chooseBook(product: Product): void {
    this.selectedProductId.set(product.product_id);
    this.selectedAuthor.set('');
    this.searchQuery.set(this.language.bookTitle(product.product_name));
    this.searchOpen.set(false);
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
