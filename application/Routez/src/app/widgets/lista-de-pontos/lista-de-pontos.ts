import { Component } from '@angular/core';
import { InputList } from "../input-list/input-list";
import { PickListService } from '../../services/PickList.service';

@Component({
  selector: 'app-lista-de-pontos',
  imports: [InputList],
  templateUrl: './lista-de-pontos.html',
  styleUrl: './lista-de-pontos.css'
})
export class ListaDePontos {
 
  constructor(
    public picklist: PickListService
  ){}
}
