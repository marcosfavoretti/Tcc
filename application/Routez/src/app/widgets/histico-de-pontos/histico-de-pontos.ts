import { Component, EventEmitter, Input, Output } from '@angular/core';
import { LocalStorageService } from '../../services/LocalStorage.service';
import { PontoDTO } from '../../../api';
import { ItemList } from "../item-list/item-list";

@Component({
  selector: 'app-histico-de-pontos',
  imports: [ItemList],
  templateUrl: './histico-de-pontos.html',
  styleUrl: './histico-de-pontos.css'
})
export class HisticoDePontos {
  @Input() tipo!: "POI" | "INICIAL";
  @Output() onPontoSelecionado: EventEmitter<PontoDTO> = new EventEmitter();
  constructor(
    private localStorageService: LocalStorageService
  ) { }

  loadHistorico(): PontoDTO[] {
    return this.tipo === 'INICIAL' ?
      this.localStorageService.consultarPontosInicial() :
      this.localStorageService.consultarPOIs()
  }
}
