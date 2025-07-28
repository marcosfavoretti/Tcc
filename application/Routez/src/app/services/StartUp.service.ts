import { Injectable } from "@angular/core";
import { RoutzAPI } from "./RoutzAPI";
import { AlgoritmoStoreService } from "./AlgoritmoStore.service";
import { tap } from "rxjs";
import { LoadingPopupService } from "./LoadingPopup.service";

@Injectable({
    providedIn: 'root'
})
export class StartUpService{
    constructor(
        private algoritoStorage: AlgoritmoStoreService,
        private api: RoutzAPI,
        private popup: LoadingPopupService
    ){}
    
    startUp():void{
        const algoritmos$ = this.api.consultaAlgoritmos()
        .pipe(
            tap(
                algoritmos => this.algoritoStorage.setAlgoritmos(algoritmos)
            )
        );
        this.popup.showWhile(algoritmos$);
    }
}