import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SelecionadorDeAlgoritmos } from './selecionador-de-algoritmos';

describe('SelecionadorDeAlgoritmos', () => {
  let component: SelecionadorDeAlgoritmos;
  let fixture: ComponentFixture<SelecionadorDeAlgoritmos>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SelecionadorDeAlgoritmos]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SelecionadorDeAlgoritmos);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
