import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AlgoritmoStoreService {
  private algoritmos: string[] = [];
  private algoritmosSelecionados: string[] = [];

  // Subjects para eventos
  private algoritmosSubject = new BehaviorSubject<string[]>([]);
  private algoritmosSelecionadosSubject = new BehaviorSubject<string[]>([]);

  // Observables públicos
  algoritmos$ = this.algoritmosSubject.asObservable();
  algoritmosSelecionados$ = this.algoritmosSelecionadosSubject.asObservable();

  getAlgoritmos(): string[] {
    return this.algoritmos;
  }

  getAlgoritmosSelecionados(): string[] {
    return this.algoritmosSelecionados;
  }

  selecionaAlgoritmosSelecionados(algoritmos: string[]): void {
    this.algoritmosSelecionados = algoritmos;
    this.algoritmosSelecionadosSubject.next(algoritmos); // 🔔 emite o evento
  }

  setAlgoritmos(algoritmos: string[]): void {
    this.algoritmos = algoritmos;
    this.algoritmosSubject.next(algoritmos); // 🔔 emite o evento
    this.selecionaAlgoritmosSelecionados(algoritmos); // opcional, dependendo da lógica
  }
}
