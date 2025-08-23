import { Component, Input, OnInit } from '@angular/core';
import { PickListService } from '../../services/PickList.service';
import { PontoDTO } from '../../../api';
import { ItemList } from "../item-list/item-list";
import { LoadingPopupService } from '../../services/LoadingPopup.service';
import { MapPopup } from '../map-popup/map-popup';
import { ColorCSS } from '../../@core/enum/Colorcss.enum';
import { PontoDtoCor } from '../../@core/types/PontoDtoCor';

@Component({
  selector: 'app-input-list',
  imports: [ItemList],
  templateUrl: './input-list.html',
  styleUrl: './input-list.css'
})
export class InputList implements OnInit{
  @Input() label!: string
  @Input() itens: PontoDtoCor[] = []
  @Input() tipo!: "POI" | "INICIAL";

  // getCor(index: number):string{
  //   const colors = Object.values(ColorCSS);
  //   if(this.tipo === 'INICIAL') return colors[colors.length-1]
  //   if (index < colors.length) {
  //     return colors[index];
  //   }
  //   const randomIndex = Math.floor(Math.random() * colors.length);
  //   return colors[randomIndex];
  // }

  constructor(
    private popup: LoadingPopupService
  ) { }

  ngOnInit(): void {}

  showForms():void{
    this.popup.showPopUpComponent(MapPopup, {tipo: this.tipo})
  }
}
