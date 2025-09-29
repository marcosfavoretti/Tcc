import { Component, input } from '@angular/core';
import { DialogModule } from 'primeng/dialog';
import {ImageModule} from "primeng/image"
@Component({
  selector: 'app-metricas',
  imports: [DialogModule, ImageModule],
  templateUrl: './metricas.html',
  styleUrl: './metricas.css'
})
//isso tera que ser mudado pois se nao ira mostrar a metrica de tudo
export class Metricas {
  metricas = input.required<{ [k: string]: string }>();

  getMetricasEntries(): any[] {
    return Object.entries(this.metricas());
  }

  isBase64Image(value: string): boolean {
    if (typeof value !== 'string') {
      return false;
    }
    // Regex para checar o formato 'data:image/...;base64,'
    const base64Regex = /^data:image\/[a-zA-Z]*;base64,/;
    return base64Regex.test(value);
  }
}
