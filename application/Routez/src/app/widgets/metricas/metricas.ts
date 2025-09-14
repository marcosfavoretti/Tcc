import { Component, input } from '@angular/core';

@Component({
  selector: 'app-metricas',
  imports: [],
  templateUrl: './metricas.html',
  styleUrl: './metricas.css'
})
//isso tera que ser mudado pois se nao ira mostrar a metrica de tudo
export class Metricas {
  metricas = input.required<{[k: string]: string}>();

  getMetricasEntries():any[]{
    return Object.entries(this.metricas());
  }
}
