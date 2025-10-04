import { Component, Input } from '@angular/core';
import { PontoDTO } from '../../../api';

@Component({
  selector: 'app-item-list',
  standalone: true,
  templateUrl: './item-list.html',
  styleUrl: './item-list.css'
})
export class ItemList {
  @Input() ponto!: PontoDTO
  @Input() cor: string = 'pink';
}
