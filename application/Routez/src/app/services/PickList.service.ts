import { Injectable, signal, computed } from "@angular/core";
import { PontoDTO } from "../../api";
import { LocalStorageService } from "./LocalStorage.service";
import { PontoDtoCor } from "../@core/types/PontoDtoCor";
import { ColorCSS } from "../@core/enum/Colorcss.enum";

@Injectable({
    providedIn: "root"
})
export class PickListService {
    constructor(private localStorage: LocalStorageService) { }

    // signals no lugar das props normais
    private _pontoInicial = signal<PontoDtoCor | undefined>(undefined);
    private _pois = signal<PontoDtoCor[]>([]);

    // computed para derivar os dados (parecido com selectors no ngrx)
    readonly pois = computed(() => this._pois());
    readonly pontoInicial = computed(() => this._pontoInicial());

    // computed agregador (substitui o EventEmitter)
    readonly state = computed(() => ({
        pois: this._pois().map(p => ({ ...p } as PontoDTO)),
        ponto_inicial: this._pontoInicial()
            ? ({ ...this._pontoInicial() } as PontoDTO)
            : undefined
    }));

    pontoInicialArray = computed(() =>
        this.pontoInicial() ? [this.pontoInicial()!] : []
    );

    addPontoInicial(ponto: PontoDTO): void {
        const pontoColorido: PontoDtoCor = {
            ...ponto,
            cor: Object.values(ColorCSS)[0]
        };
        this._pontoInicial.set(pontoColorido);
        this.localStorage.setItem<PontoDTO>(`I-${ponto.name}`, ponto);
    }

    addPOIs(ponto: PontoDTO): void {
        if (this.pois().some(poi => poi.name === ponto.name)) { alert('nao é possivel adicionar dois pontos com o mesmo nome'); return };
        const pontoColorido: PontoDtoCor = {
            ...ponto,
            cor: Object.values(ColorCSS)[this._pois().length + 1]
        };
        this._pois.update(pois => [...pois, pontoColorido]);
        this.localStorage.setItem<PontoDTO>(`POI-${ponto.name}`, ponto);
    }

    removePontoInicial() {
        this._pontoInicial.set(undefined);
    }

    removePOIs(ponto: PontoDtoCor): void {
        console.log(ponto)
        this._pois.update(pois => pois.filter(p => p.name !== ponto.name));
        console.log(this._pois())
    }
}
