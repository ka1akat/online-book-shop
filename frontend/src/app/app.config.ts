// Настройки всего приложения Angular.

import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { TitleStrategy, provideRouter, withComponentInputBinding } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';

import { routes } from './app.routes';
import { ShopTitleStrategy } from './services/language.service';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes, withComponentInputBinding()), // :id из адреса попадает в input()
    provideHttpClient(), // нужен, чтобы ApiService мог делать запросы к Django
    { provide: TitleStrategy, useClass: ShopTitleStrategy }, // заголовок вкладки на выбранном языке
  ],
};
