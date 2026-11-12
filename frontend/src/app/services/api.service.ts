// ApiService — единственное место, где Angular общается с Django.
// Каждый метод = один адрес API из backend/shop/urls.py.

import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { CartLine, Category, CustomerForm, Order, Product } from '../models';

const API = 'http://localhost:8000/api';

export interface RegisterForm {
  full_name: string;
  email: string;
  password: string;
}

export interface RegisteredUser {
  id: number;
  full_name: string;
  email: string;
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);

  getProducts(): Observable<Product[]> {
    return this.http.get<Product[]>(`${API}/products/`);
  }

  getCategories(): Observable<Category[]> {
    return this.http.get<Category[]>(`${API}/categories/`);
  }

  getProductsByCategory(categoryId: number | null): Observable<Product[]> {
    const url = categoryId === null ? `${API}/products/` : `${API}/products/?category_id=${categoryId}`;
    return this.http.get<Product[]>(url);
  }

  createOrder(customer: CustomerForm, lines: CartLine[]): Observable<Order> {
    return this.http.post<Order>(`${API}/orders/`, {
      customer: { full_name: customer.full_name, email: customer.email, phone: customer.phone },
      items: lines.map((l) => ({ product_id: l.product.product_id, quantity: l.quantity })),
      delivery_method: customer.delivery_method,
      address: {
        city: customer.city,
        full_address: customer.full_address,
        within_city: customer.within_city,
        entrance: customer.entrance,
        apartment: customer.apartment,
        intercom_code: customer.intercom_code,
        floor: customer.floor,
      },
    });
  }

  getOrder(id: number): Observable<Order> {
    return this.http.get<Order>(`${API}/orders/${id}/`);
  }

  payOrder(id: number, cardNumber: string): Observable<Order> {
    return this.http.post<Order>(`${API}/orders/${id}/pay/`, { card_number: cardNumber });
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

