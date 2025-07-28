import { Component, OnInit } from '@angular/core';
import { ListboxModule } from 'primeng/listbox';
import { AlgoritmoStoreService } from '../../services/AlgoritmoStore.service';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-selecionador-de-algoritmos',
  standalone: true,
  imports: [ListboxModule, FormsModule],
  templateUrl: './selecionador-de-algoritmos.html',
  styleUrls: ['./selecionador-de-algoritmos.css']
})
export class SelecionadorDeAlgoritmos implements OnInit {
  algoritmos: { name: string }[] = [];
  algoritmosSelecionados: { name: string }[] = [];

  constructor(private algoritmoStoreService: AlgoritmoStoreService) {}

  ngOnInit(): void {
    this.algoritmoStoreService.algoritmos$.subscribe(lista => {
      this.algoritmos = lista.map(t => ({ name: t }));
    });

    this.algoritmoStoreService.algoritmosSelecionados$.subscribe(selecionados => {
      this.algoritmosSelecionados = selecionados.map(t => ({ name: t }));
    });
  }

  onSelecionadosChange(): void {
    const nomesSelecionados = this.algoritmosSelecionados.map(item => item.name);
    this.algoritmoStoreService.selecionaAlgoritmosSelecionados(nomesSelecionados);
  }
}
