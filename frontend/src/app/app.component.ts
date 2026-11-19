// Корневой компонент: шапка сайта + место, куда роутер вставляет текущую страницу.

import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AccountService } from './services/account.service';
import { AuthService } from './services/auth.service';
import { CartService } from './services/cart.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './app.component.html',
})
export class AppComponent {
  cart = inject(CartService);
  auth = inject(AuthService);
  account = inject(AccountService); // счётчики уведомлений и избранного в меню
}
