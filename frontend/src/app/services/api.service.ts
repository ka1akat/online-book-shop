// ApiService — единственное место, где Angular общается с Django.
// Каждый метод = один адрес API из backend/shop/urls.py.

import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { CartLine, CustomerForm, Order, Product } from '../models';

const API = 'http://localhost:8000/api';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);

  getProducts(): Observable<Product[]> {
    return this.http.get<Product[]>(`${API}/products/`);
  }

  createOrder(customer: CustomerForm, lines: CartLine[]): Observable<Order> {
    return this.http.post<Order>(`${API}/orders/`, {
      customer,
      items: lines.map((l) => ({ product_id: l.product.product_id, quantity: l.quantity })),
    });
  }

  getOrder(id: number): Observable<Order> {
    return this.http.get<Order>(`${API}/orders/${id}/`);
  }

  payOrder(id: number, cardNumber: string): Observable<Order> {
    return this.http.post<Order>(`${API}/orders/${id}/pay/`, { card_number: cardNumber });
  }
}

// Достаёт понятный текст ошибки из ответа Django
export function errorText(err: HttpErrorResponse): string {
  if (err.status === 0) {
    return 'Нет связи с сервером. Запущен ли Django (python manage.py runserver)?';
  }
  const body = err.error;
  if (body?.detail) return body.detail;
  if (body && typeof body === 'object') {
    return 'Проверьте поля формы: ' + Object.keys(body).join(', ');
  }
  return 'Что-то пошло не так. Попробуйте ещё раз.';
}
