import { Component, OnInit } from '@angular/core';
import { ListaDePontos } from "../lista-de-pontos/lista-de-pontos";
import { RoutzAPI } from '../../services/RoutzAPI';
import { forkJoin, Observable, tap } from 'rxjs';
import { LoadingPopupService } from '../../services/LoadingPopup.service';
import { AlgoritmosResponseDto, TipoAlgoritmoEnum } from '../../../api';
import { PickListService } from '../../services/PickList.service';
import { GerenciaAlgoritmoResService } from '../../services/GerenciaAlgoritmoRes.service';
import { AlgoritmoStoreService } from '../../services/AlgoritmoStore.service';
import { PopoverModule } from 'primeng/popover';
import { SelecionadorDeAlgoritmos } from "../selecionador-de-algoritmos/selecionador-de-algoritmos";

@Component({
  selector: 'app-side-bar',
  imports: [ListaDePontos, PopoverModule, SelecionadorDeAlgoritmos],
  templateUrl: './side-bar.html',
  styleUrl: './side-bar.css'
})
export class SideBar {

  constructor(
    private api: RoutzAPI,
    private algoritmoStorage: AlgoritmoStoreService,
    private popup: LoadingPopupService,
    private pickList: PickListService,
    private gerenciaAlgoritmoRes: GerenciaAlgoritmoResService
  ) { }

  requestAlgoritmo(): void {
    if (!this.pickList.ponto_inicial) {
      alert('Adicione um ponto inicial')
      return;
    }
    if (this.pickList.pois.length < 1) {
      alert('Adicione mais pontos de interesse')
      return;
    }
    const requests: Observable<AlgoritmosResponseDto>[] = [];
    for (const algoritmo of this.algoritmoStorage.getAlgoritmosSelecionados()) {
      const resposta$ = this.api.executaAlgoritmo({
        algoritmo: algoritmo as TipoAlgoritmoEnum,
        ponto_inicial: this.pickList.ponto_inicial,
        pontos_interesse: this.pickList.pois,
      })
      requests.push(resposta$);
    }
    const allResponses$ = forkJoin(requests)
      .pipe(
        tap(
          data => this.gerenciaAlgoritmoRes.setRespostas(data)
        )
      );
    this.popup.showWhile(allResponses$);
    allResponses$.subscribe({
      next: (responses) => {
        console.log('Todas as respostas:', responses);
      },
      error: (err) => {
        console.error('Erro na requisição:', err);
      }
    });
  }

}
