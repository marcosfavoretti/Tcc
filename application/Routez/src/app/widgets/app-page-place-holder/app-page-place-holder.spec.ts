import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AppPagePlaceHolder } from './app-page-place-holder';

describe('AppPagePlaceHolder', () => {
  let component: AppPagePlaceHolder;
  let fixture: ComponentFixture<AppPagePlaceHolder>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AppPagePlaceHolder]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AppPagePlaceHolder);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
