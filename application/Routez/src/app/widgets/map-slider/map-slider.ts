import { Component, computed, Signal } from '@angular/core';
import { CarouselModule } from "primeng/carousel";
import { GerenciaAlgoritmoResService } from '../../services/GerenciaAlgoritmoRes.service';
import { Map } from "../map/map";
import { Metricas } from "../metricas/metricas";
import { PickListService } from '../../services/PickList.service';
import { AsyncPipe, CommonModule } from '@angular/common';
import { catchError, map, Observable, of, startWith } from 'rxjs';
import { AlgoritmosResponseDto } from '../../../api';

// Interface para representar o estado do nosso dado
interface StreamState<T> {
  value?: T;
  error?: any;
  loading?: boolean;
}

@Component({
  selector: 'app-map-slider',
  standalone: true, // Adicionado para conformidade com a estrutura de imports
  imports: [CarouselModule, Map, Metricas, AsyncPipe, CommonModule],
  templateUrl: './map-slider.html',
  styleUrl: './map-slider.css'
})
export class MapSlider {

  public readonly respostasComEstado: Signal<Observable<StreamState<AlgoritmosResponseDto>>[]>;

  constructor(
    public readonly gerenciaAlgoritmoResService: GerenciaAlgoritmoResService,
    public readonly pickListService: PickListService // Adicionado para o template
  ) {
    this.respostasComEstado = computed(() => {
      const respostas$ = this.gerenciaAlgoritmoResService.respostas$();

      return respostas$.map(obs =>
        obs.pipe(
          map(value => ({ value, loading: false })),
          startWith({ loading: true }),
          catchError(error => of({ error, loading: false }))
        )
      );
    });
  }

  /**
   * Workaround para restaurar a tipagem forte dentro do ng-template do PrimeNG.
   * @param obs O Observable que perdeu a tipagem.
   * @returns O mesmo Observable, mas com a tipagem correta.
   */
  castObs(obs: Observable<any>): Observable<StreamState<AlgoritmosResponseDto>> {
    return obs as Observable<StreamState<AlgoritmosResponseDto>>;
  }
}