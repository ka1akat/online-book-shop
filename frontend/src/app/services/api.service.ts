// ApiService — единственное место, где Angular общается с Django.
// Каждый метод = один адрес API из backend/shop/urls.py.

import { HttpClient, HttpErrorResponse, HttpHeaders, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { CartLine, Category, CustomerForm, Order, Product, ProductFilters, Review, SavedAddress, StockRequestNotice, StoreReview, SupportRequest, SupportTicket, } from '../models';

import { environment } from '../../environments/environment';

// localhost:8000 на своём компьютере, адрес Render на сервере (src/environments/)
const API = environment.apiUrl;

export interface RegisterForm {
  full_name: string;
  email: string;
  password: string;
}

export interface RegisteredUser {
  id: number;
  full_name: string;
  email: string;
  token?: string; // подписанный Django токен; нужен, чтобы писать отзывы
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);

  // Без фильтров — все книги. С фильтрами получится адрес вида
  // /api/products/?category_id=2&min_price=3000&min_rating=4&ordering=-rating
  getProducts(filters?: ProductFilters): Observable<Product[]> {
    let params = new HttpParams();
    if (filters) {
      for (const [key, value] of Object.entries(filters)) {
        if (value !== null && value !== '') {
          params = params.set(key, String(value));
        }
      }
    }
    return this.http.get<Product[]>(`${API}/products/`, { params });
  }

  getProduct(productId: string): Observable<Product> {
    return this.http.get<Product>(`${API}/products/${productId}/`);
  }

  // Токен необязателен: с ним Django отметит мой отзыв флажком is_mine
  getReviews(productId: string, token?: string): Observable<Review[]> {
    const headers = token ? new HttpHeaders({ Authorization: `Bearer ${token}` }) : undefined;
    return this.http.get<Review[]>(`${API}/products/${productId}/reviews/`, { headers });
  }

  // Токен идёт в заголовке Authorization: так Django понимает, кто пишет отзыв
  addReview(productId: string, rating: number, comment: string, token: string): Observable<Review> {
    const headers = new HttpHeaders({ Authorization: `Bearer ${token}` });
    return this.http.post<Review>(
      `${API}/products/${productId}/reviews/`, { rating, comment }, { headers },
    );
  }

  getStoreReviews(token?: string): Observable<StoreReview[]> {
    const headers = token ? new HttpHeaders({ Authorization: `Bearer ${token}` }) : undefined;
    return this.http.get<StoreReview[]>(`${API}/store-reviews/`, { headers });
  }

  addStoreReview(rating: number, comment: string, token: string): Observable<StoreReview> {
    const headers = new HttpHeaders({ Authorization: `Bearer ${token}` });
    return this.http.post<StoreReview>(`${API}/store-reviews/`, { rating, comment }, { headers });
  }

  getCategories(): Observable<Category[]> {
    return this.http.get<Category[]>(`${API}/categories/`);
  }

  getSavedAddresses(email: string, token: string): Observable<SavedAddress[]> {
    const params = new HttpParams().set('email', email);
    const headers = new HttpHeaders({ Authorization: `Bearer ${token}` });
    return this.http.get<SavedAddress[]>(`${API}/addresses/`, { params, headers });
  }


  createOrder(customer: CustomerForm, lines: CartLine[], token?: string): Observable<Order> {
    const payload: Record<string, unknown> = {
      customer: { full_name: customer.full_name, email: customer.email, phone: customer.phone },
      items: lines.map((l) => ({ product_id: l.product.product_id, quantity: l.quantity })),
      delivery_method: customer.delivery_method,
      save_address: customer.save_address ?? false,
    };
    if (customer.saved_address_id) {
      payload['saved_address_id'] = customer.saved_address_id;
    } else {
      payload['address'] = {
        city: customer.city,
        full_address: customer.full_address,
        within_city: customer.within_city,
        entrance: customer.entrance,
        apartment: customer.apartment,
        intercom_code: customer.intercom_code,
        floor: customer.floor,
      };
    }
    const headers = customer.saved_address_id && token
      ? new HttpHeaders({ Authorization: `Bearer ${token}` })
      : undefined;
    return this.http.post<Order>(`${API}/orders/`, payload, { headers });
  }

  getOrder(id: number): Observable<Order> {
    return this.http.get<Order>(`${API}/orders/${id}/`);
  }

  payOrder(id: number, cardNumber: string): Observable<Order> {
    return this.http.post<Order>(`${API}/orders/${id}/pay/`, { card_number: cardNumber });
  }
  
  // Обращение в поддержку по заказу. Если покупатель вошёл, токен в заголовке Authorization
  // подсказывает Django, чей это заказ; иначе нужен email из заказа в теле запроса.
  sendSupportRequest(request: SupportRequest, token?: string): Observable<SupportTicket> {
    const headers = token ? new HttpHeaders({ Authorization: `Bearer ${token}` }) : undefined;
    return this.http.post<SupportTicket>(`${API}/support/`, request, { headers });
  }

  // ---------- Лист ожидания «Notify me» и уведомления (FR-07) ----------

  // Вошедшего покупателя Django узнаёт по токену; гость передаёт email
  notifyMe(productId: string, email: string, token?: string): Observable<StockRequestNotice> {
    const headers = token ? new HttpHeaders({ Authorization: `Bearer ${token}` }) : undefined;
    return this.http.post<StockRequestNotice>(`${API}/products/${productId}/notify/`, { email }, { headers });
  }

  stopWaiting(productId: string, token: string): Observable<void> {
    const headers = new HttpHeaders({ Authorization: `Bearer ${token}` });
    return this.http.delete<void>(`${API}/products/${productId}/notify/`, { headers });
  }

  getNotifications(token: string): Observable<StockRequestNotice[]> {
    const headers = new HttpHeaders({ Authorization: `Bearer ${token}` });
    return this.http.get<StockRequestNotice[]>(`${API}/notifications/`, { headers });
  }

  markNotificationsRead(token: string): Observable<{ marked_read: number }> {
    const headers = new HttpHeaders({ Authorization: `Bearer ${token}` });
    return this.http.post<{ marked_read: number }>(`${API}/notifications/read/`, {}, { headers });
  }

  // ---------- Мои заказы ----------

  getMyOrders(token: string): Observable<Order[]> {
    const headers = new HttpHeaders({ Authorization: `Bearer ${token}` });
    return this.http.get<Order[]>(`${API}/my-orders/`, { headers });
  }

  // ---------- Wishlist (избранное) ----------

  getWishlist(token: string): Observable<Product[]> {
    const headers = new HttpHeaders({ Authorization: `Bearer ${token}` });
    return this.http.get<Product[]>(`${API}/wishlist/`, { headers });
  }

  addToWishlist(productId: string, token: string): Observable<unknown> {
    const headers = new HttpHeaders({ Authorization: `Bearer ${token}` });
    return this.http.post(`${API}/wishlist/`, { product_id: productId }, { headers });
  }

  removeFromWishlist(productId: string, token: string): Observable<void> {
    const headers = new HttpHeaders({ Authorization: `Bearer ${token}` });
    return this.http.delete<void>(`${API}/wishlist/${productId}/`, { headers });
  }

  register(form: RegisterForm): Observable<RegisteredUser> {
    return this.http.post<RegisteredUser>(`${API}/register/`, form);
  }
  login(email: string, password: string): Observable<RegisteredUser> {
    return this.http.post<RegisteredUser>(`${API}/login/`, { email, password });
  }
}

// Достаёт понятный текст ошибки из ответа Django
export function errorText(err: HttpErrorResponse): string {
  if (err.status === 0) {
    return 'Cannot reach the server. Is Django running (python manage.py runserver)?';
  }
  const body = err.error;
  if (body?.detail) return body.detail;
  if (body && typeof body === 'object') {
    return Object.values(body).flat().join(' ');
  }
  return 'Something went wrong. Please try again.';
}

