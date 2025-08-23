import { Component, Input } from '@angular/core';
import { GerenciaAlgoritmoResService } from '../../services/GerenciaAlgoritmoRes.service';

@Component({
  selector: 'app-metricas',
  imports: [],
  templateUrl: './metricas.html',
  styleUrl: './metricas.css'
})
//isso tera que ser mudado pois se nao ira mostrar a metrica de tudo
export class Metricas {
  @Input() metricas: any[] = [];

  getMetricasEntries():any[]{
    return Object.entries(this.metricas);
  }
}
