import { Component } from '@angular/core';
import { GerenciaAlgoritmoResService } from '../../services/GerenciaAlgoritmoRes.service';

@Component({
  selector: 'app-metricas',
  imports: [],
  templateUrl: './metricas.html',
  styleUrl: './metricas.css'
})
//isso tera que ser mudado pois se nao ira mostrar a metrica de tudo
export class Metricas {
  constructor(
    public gerenciaAlgoritmoResService: GerenciaAlgoritmoResService
  ){}

  getMetricasEntries(): [string, any][] {
    return this.gerenciaAlgoritmoResService.respostas
      .flatMap(r => Object.entries(r.metricas));
  }
}
