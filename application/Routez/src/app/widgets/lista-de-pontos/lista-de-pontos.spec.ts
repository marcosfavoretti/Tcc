import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListaDePontos } from './lista-de-pontos';

describe('ListaDePontos', () => {
  let component: ListaDePontos;
  let fixture: ComponentFixture<ListaDePontos>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ListaDePontos]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ListaDePontos);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
