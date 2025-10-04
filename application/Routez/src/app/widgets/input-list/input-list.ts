import { Component, inject, input, Input, OnInit, Signal } from '@angular/core';
import { PickListService } from '../../services/PickList.service';
import { ItemList } from "../item-list/item-list";
import { LoadingPopupService } from '../../services/LoadingPopup.service';
import { MapPopup } from '../map-popup/map-popup';
import { PontoDtoCor } from '../../@core/types/PontoDtoCor';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-input-list',
  standalone: true,
  imports: [CommonModule, ItemList],
  templateUrl: './input-list.html',
  styleUrl: './input-list.css'
})
export class InputList implements OnInit {
  @Input() label!: string
  @Input() tipo!: "POI" | "INICIAL";
  @Input() itens!: Signal<PontoDtoCor[]>;

  pickListService = inject(PickListService);

  constructor(
    private popup: LoadingPopupService
  ) { }

  ngOnInit(): void { }

  removePoint(item: PontoDtoCor) {
    if (this.tipo === 'INICIAL') return this.pickListService.removePontoInicial();
    this.pickListService.removePOIs(item);
  }

  showForms(): void {
    this.popup.showPopUpComponent(MapPopup, { tipo: this.tipo })
  }
}
