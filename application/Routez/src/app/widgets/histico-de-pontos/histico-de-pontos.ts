import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { PontoDTO } from '../../../api';
import { PoiStoreService } from '../../services/PoiStore.service';
import { ItemList } from '../item-list/item-list';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-historico-de-pontos',
  standalone: true,
  imports: [CommonModule, ItemList],
  templateUrl: './histico-de-pontos.html',
  styleUrl: './histico-de-pontos.css'
})
export class HistoricoDePontosComponent implements OnInit {
  pontos: PontoDTO[] = [];
  @Output() onPontoSelecionado = new EventEmitter<PontoDTO>();

  constructor(private poiStore: PoiStoreService) {}

  ngOnInit(): void {
    this.poiStore.pois$.subscribe(pois => {
      this.pontos = pois;
    });
    this.poiStore.loadPOIs();
  }
}
