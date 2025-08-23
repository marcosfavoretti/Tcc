import { Component, Input } from '@angular/core';
import { CarouselModule } from "primeng/carousel"
import { GerenciaAlgoritmoResService } from '../../services/GerenciaAlgoritmoRes.service';
import { Map } from "../map/map";
import { Metricas } from "../metricas/metricas";
import { PickListService } from '../../services/PickList.service';
@Component({
  selector: 'app-map-slider',
  imports: [CarouselModule, Map, Metricas],
  templateUrl: './map-slider.html',
  styleUrl: './map-slider.css'
})
export class MapSlider {
  
  constructor(
    public pickListService: PickListService,
    public gerenciaAlgoritmoResService: GerenciaAlgoritmoResService
  ){}
}
