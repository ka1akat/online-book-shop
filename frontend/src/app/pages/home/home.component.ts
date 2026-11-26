import { Component, OnInit, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { BookTileComponent } from '../../book-tile.component';
import { Product } from '../../models';

@Component({
  selector: 'app-home',
  imports: [RouterLink, BookTileComponent],
  templateUrl: './home.component.html',
})
export class HomeComponent implements OnInit {
  private api = inject(ApiService);

  // 4 лучшие книги по оценкам для блока «Top rated» на главной
  topRated = signal<Product[]>([]);

  ngOnInit(): void {
    this.api.getTopRated(4).subscribe({ next: (list) => this.topRated.set(list), error: () => {} });
  }
}
