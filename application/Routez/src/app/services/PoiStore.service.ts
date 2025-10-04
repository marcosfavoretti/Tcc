import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { PontoDTO } from '../../api';
import { RoutzAPI } from './RoutzAPI';

@Injectable({
  providedIn: 'root'
})
export class PoiStoreService {
  private poisSubject = new BehaviorSubject<PontoDTO[]>([]);
  pois$: Observable<PontoDTO[]> = this.poisSubject.asObservable();

  constructor(private routzApi: RoutzAPI) { }

  loadPOIs(): void {
    this.routzApi.consultaPOIs().subscribe(pois => {
      this.poisSubject.next(pois);
    });
  }

  getPOIs(): PontoDTO[] {
    return this.poisSubject.getValue();
  }
}
