import { Injectable, signal } from "@angular/core";
import { AlgoritmosResponseDto } from "../../api";
import { Observable } from "rxjs";

@Injectable({
  providedIn: "root"
})
export class GerenciaAlgoritmoResService {
  // agora são signals
  respostas = signal<AlgoritmosResponseDto[]>([]);

  respostas$ = signal<Observable<AlgoritmosResponseDto>[]>([]);

  addRespostaObserver(resposta$: Observable<AlgoritmosResponseDto>): void {
    this.respostas$.update((atual) => [...atual, resposta$]);
    console.log('adionado')
  }

  addResposta(resposta: AlgoritmosResponseDto): void {
    this.respostas.update((atual) => [...atual, resposta]);
    console.log(this.respostas())
  }

  setRespostas(respostas: AlgoritmosResponseDto[]): void {
    this.respostas.set(respostas);
  }

  clearMaps(): void {
    this.respostas$.set([]);
    this.respostas.set([]);
  }
}
