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
    if (!this.pickList.pontoInicial()) {
      alert('Adicione um ponto inicial')
      return;
    }
    if (this.pickList.pois().length < 1) {
      alert('Adicione mais pontos de interesse')
      return;
    }
    const requests: Observable<AlgoritmosResponseDto>[] = [];

    this.gerenciaAlgoritmoRes.clearMaps();

    for (const algoritmo of this.algoritmoStorage.getAlgoritmosSelecionados()) {
      const resposta$ = this.api.executaAlgoritmo({
        algoritmo: algoritmo as TipoAlgoritmoEnum,
        ponto_inicial: this.pickList.pontoInicial()!,
        pontos_interesse: this.pickList.pois(),
      });
      this.gerenciaAlgoritmoRes.addRespostaObserver(resposta$);
      requests.push(resposta$);
      // .pipe(
      //   tap(res => this.gerenciaAlgoritmoRes.addResposta(res))
      // )
      // .subscribe();

      // this.gerenciaAlgoritmoRes.addRespostaObserver(
      //   this.api.executaAlgoritmo(
      //     {
      //       algoritmo: algoritmo as TipoAlgoritmoEnum,
      //       ponto_inicial: this.pickList.ponto_inicial,
      //       pontos_interesse: this.pickList.pois,
      //     }
      //   )
      // )
      // requests.push(resposta$);
    }

    // this.popup.showWhile(...requests);
  }

}
