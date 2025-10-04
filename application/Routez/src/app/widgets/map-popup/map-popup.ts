import { Component, Input, signal, ViewChild } from '@angular/core';
import { Map } from "../map/map";
import { PontoDTO } from '../../../api';
import { FormsModule, NgForm } from '@angular/forms';
import { PickListService } from '../../services/PickList.service';
import { TabsModule } from 'primeng/tabs';
import { HistoricoDePontosComponent } from "../histico-de-pontos/histico-de-pontos";
import { StepperModule } from "primeng/stepper"
import { Button } from "primeng/button"

@Component({
  selector: 'app-map-popup',
  imports: [Map, Button, FormsModule, TabsModule, HistoricoDePontosComponent, StepperModule],
  providers: [],
  standalone: true,
  templateUrl: './map-popup.html',
  styleUrl: './map-popup.css'
})
export class MapPopup {
  constructor(
    public pickListService: PickListService
  ) { }

  @Input() closeButtonFn!: () => void;
  @Input() tipo!: "POI" | "INICIAL";
  ponto = signal<Partial<PontoDTO> | undefined>(undefined);

  setPonto(ponto: Partial<PontoDTO>):void{
    this.ponto.set(ponto);
    console.log(this.ponto())
  }

  submitPontos(form: NgForm): void {
    if (!form.valid) throw new Error('formulario invalido');
    const dto = ({
      latitude: form.controls['latitude'].value,
      longitude: form.controls['longitude'].value,
      name: form.controls['nome'].value
    });
    this.tipo === 'POI' ?
      this.pickListService.addPOIs(dto)
      : this.pickListService.addPontoInicial(dto)
    this.closeButtonFn();
  }

  submitPontoAntigo(ponto: PontoDTO): void {
    this.tipo === 'POI' ?
      this.pickListService.addPOIs(ponto)
      : this.pickListService.addPontoInicial(ponto);
    this.closeButtonFn();
  }

}
