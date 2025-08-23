import { EventEmitter, Injectable } from "@angular/core";
import { PontoDTO } from "../../api";
import { LocalStorageService } from "./LocalStorage.service";
import { PontoDtoCor } from "../@core/types/PontoDtoCor";
import { ColorCSS } from "../@core/enum/Colorcss.enum";

@Injectable({
    providedIn: 'root'
})
export class PickListService {

    constructor(
        private localStorage: LocalStorageService
    ) { }

    ponto_inicial?: PontoDtoCor;
    pois: PontoDtoCor[] = [];

    changeEvent: EventEmitter<{
        pois: PontoDTO[],
        ponto_inicial: PontoDTO
    }> = new EventEmitter();


    addPontoInicial(ponto: PontoDTO): void {
        const pontoColorido: PontoDtoCor = {
            ...ponto,
            cor: Object.values(ColorCSS)[0]
        }
        this.ponto_inicial = pontoColorido;
        this.localStorage.setItem<PontoDTO>(`I-${ponto.name}`, ponto)
    }

    addPOIs(ponto: PontoDTO): void {
        const pontoColorido: PontoDtoCor = {
            ...ponto,
            cor: Object.values(ColorCSS)[this.pois.length + 1]
        }
        this.pois.push(pontoColorido);
        this.localStorage.setItem<PontoDTO>(`POI-${ponto.name}`, ponto)
    }

    removePOIs(ponto: PontoDtoCor): void {
        const targetIndex = this.pois.findIndex(p => p === ponto);
        this.pois.splice(targetIndex);
    }
}