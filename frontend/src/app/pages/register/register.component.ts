import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ApiService, RegisteredUser, errorText } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-register',
  imports: [FormsModule, RouterLink],
  templateUrl: './register.component.html',
})
export class RegisterComponent {
  private api = inject(ApiService);
  private auth = inject(AuthService);

  fullName = '';
  email = '';
  password = '';

  sending = signal(false);
  error = signal('');
  user = signal<RegisteredUser | null>(null);

  submit(): void {
    this.sending.set(true);
    this.error.set('');
    this.api
      .register({ full_name: this.fullName, email: this.email, password: this.password })
      .subscribe({
        next: (user) => {
          this.auth.setUser(user);
          this.user.set(user);
          this.password = '';
          this.sending.set(false);
        },
        error: (err) => {
          this.error.set(errorText(err));
          this.sending.set(false);
        },
      });
  }
}