import { Injectable } from "@angular/core";
import { AlgoritmosResponseDto } from "../../api";

@Injectable({
    providedIn: 'root'
})
export class GerenciaAlgoritmoResService{
    respostas: AlgoritmosResponseDto[] = []

    addResposta(resposta: AlgoritmosResponseDto):void{
        this.respostas.push(resposta);
    }

    
}