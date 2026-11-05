import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ApiService, errorText } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  imports: [FormsModule, RouterLink],
  templateUrl: './login.component.html',
})
export class LoginComponent {
  private api = inject(ApiService);
  private auth = inject(AuthService);
  private router = inject(Router);

  email = '';
  password = '';
  sending = signal(false);
  error = signal('');

  submit(): void {
    this.sending.set(true);
    this.error.set('');
    this.api.login(this.email, this.password).subscribe({
      next: (user) => {
        this.auth.setUser(user);
        this.router.navigate(['/catalog']);
      },
      error: (err) => {
        this.error.set(errorText(err));
        this.sending.set(false);
      },
    });
  }
}