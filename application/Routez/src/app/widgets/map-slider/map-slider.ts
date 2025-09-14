import { Component, Input } from '@angular/core';
import { CarouselModule } from "primeng/carousel"
import { GerenciaAlgoritmoResService } from '../../services/GerenciaAlgoritmoRes.service';
import { Map } from "../map/map";
import { Metricas } from "../metricas/metricas";
import { PickListService } from '../../services/PickList.service';
import { AsyncPipe, CommonModule } from '@angular/common';
import { firstValueFrom, from, Observable } from 'rxjs';
import { AlgoritmosResponseDto } from '../../../api';
@Component({
  selector: 'app-map-slider',
  imports: [CarouselModule, Map, Metricas, AsyncPipe, CommonModule],
  templateUrl: './map-slider.html',
  styleUrl: './map-slider.css'
})
export class MapSlider {

  constructor(
    public pickListService: PickListService,
    public gerenciaAlgoritmoResService: GerenciaAlgoritmoResService
  ) { }

  castObs(obs: Observable<AlgoritmosResponseDto>): Observable<AlgoritmosResponseDto> {
    return obs;
  }
}
