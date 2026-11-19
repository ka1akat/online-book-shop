// Охранники маршрутов (Angular Router: CanActivateFn).
// accountGuard: личный кабинет только для тех, кто вошёл — иначе отправляем на /login.
// toAccount: старые адреса (/my-orders, /wishlist...) у вошедшего пользователя ведут в кабинет.

import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from './services/auth.service';

export const accountGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  return auth.user() ? true : inject(Router).createUrlTree(['/login']);
};

export function toAccount(section: string): CanActivateFn {
  return () => {
    const auth = inject(AuthService);
    return auth.user() ? inject(Router).createUrlTree(['/account', section]) : true;
  };
}
