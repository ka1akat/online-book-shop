// AuthService запоминает, кто вошёл на сайт. Пароль здесь не хранится.

import { Injectable, signal } from '@angular/core';
import { RegisteredUser } from './api.service';

const KEY = 'bookshop_user';

@Injectable({ providedIn: 'root' })
export class AuthService {
  user = signal<RegisteredUser | null>(this.load());

  setUser(user: RegisteredUser): void {
    this.user.set(user);
    try {
      localStorage.setItem(KEY, JSON.stringify(user));
    } catch {
      /* браузер запретил хранилище: вход сохранится до обновления страницы */
    }
  }

  logout(): void {
    this.user.set(null);
    try {
      localStorage.removeItem(KEY);
    } catch {
      /* хранилище недоступно: удалять нечего */
    }
  }

  private load(): RegisteredUser | null {
    try {
      const saved = localStorage.getItem(KEY);
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  }
}