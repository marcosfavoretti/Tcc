import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HisticoDePontos } from './histico-de-pontos';

describe('HisticoDePontos', () => {
  let component: HisticoDePontos;
  let fixture: ComponentFixture<HisticoDePontos>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HisticoDePontos]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HisticoDePontos);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
