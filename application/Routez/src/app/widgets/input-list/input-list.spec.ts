import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InputList } from './input-list';

describe('InputList', () => {
  let component: InputList;
  let fixture: ComponentFixture<InputList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [InputList]
    })
    .compileComponents();

    fixture = TestBed.createComponent(InputList);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
