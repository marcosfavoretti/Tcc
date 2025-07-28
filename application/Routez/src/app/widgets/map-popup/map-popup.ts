import { Component, Input, ViewChild } from '@angular/core';
import { Map } from "../map/map";
import { PontoDTO } from '../../../api';
import { FormsModule, NgForm } from '@angular/forms';
import { PickListService } from '../../services/PickList.service';
import { TabsModule } from 'primeng/tabs';

@Component({
  selector: 'app-map-popup',
  imports: [Map, FormsModule, TabsModule],
  providers: [],
  standalone: true,
  templateUrl: './map-popup.html',
  styleUrl: './map-popup.css'
})
export class MapPopup {
  constructor(
    public pickListService: PickListService
  ) { }

  submitPontos(form: NgForm): void {
    if (!form.valid) throw new Error('formulario invalido')
    console.log(
      {
        latitude: form.controls['latitude'].value,
        longitude: form.controls['longitude'].value,
        name: form.controls['nome'].value
      },
    )
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

  @Input() closeButtonFn!: () => void;
  @Input() tipo!: "POI" | "INICIAL";
  ponto!: Partial<PontoDTO>;
}
