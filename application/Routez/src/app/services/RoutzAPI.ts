import { Injectable } from "@angular/core";
import { from, Observable } from "rxjs";
import { algoritmosDisponiveisAlgoritmosGet, AlgoritmosDto, AlgoritmosResponseDto, calcularRotaAlgoritmosPost, getAllPoisPoisGet, PontoDTO } from "../../api";

@Injectable({
    providedIn: 'root'
})
export class RoutzAPI {
    executaAlgoritmo(dto: AlgoritmosDto): Observable<AlgoritmosResponseDto> {
        return from(
            calcularRotaAlgoritmosPost(dto)
        )
    }

    consultaAlgoritmos(): Observable<string[]> {
        return from(
            algoritmosDisponiveisAlgoritmosGet()
        )
    }

    consultaPOIs(): Observable<PontoDTO[]> {
        return from(
            getAllPoisPoisGet()
        )
    }
}