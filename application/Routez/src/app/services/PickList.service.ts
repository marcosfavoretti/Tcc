import { EventEmitter, Injectable } from "@angular/core";
import { PontoDTO } from "../../api";
import { LocalStorageService } from "./LocalStorage.service";

@Injectable({
    providedIn: 'root'
})
export class PickListService {

    constructor(
        private localStorage: LocalStorageService
    ) { }

    ponto_inicial?: PontoDTO;
    pois: PontoDTO[] = [];

    changeEvent: EventEmitter<{
        pois: PontoDTO[],
        ponto_inicial: PontoDTO
    }> = new EventEmitter();


    addPontoInicial(ponto: PontoDTO): void {
        this.ponto_inicial = ponto;
        this.localStorage.setItem<PontoDTO>(`I-${ponto.name}`, ponto)
    }

    addPOIs(ponto: PontoDTO): void {
        this.pois.push(ponto);
        this.localStorage.setItem<PontoDTO>(`POI-${ponto.name}`, ponto)
    }

    removePOIs(ponto: PontoDTO): void {
        const targetIndex = this.pois.findIndex(p => p === ponto);
        this.pois.splice(targetIndex);
    }
}