import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MapSlider } from './map-slider';

describe('MapSlider', () => {
  let component: MapSlider;
  let fixture: ComponentFixture<MapSlider>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MapSlider]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MapSlider);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
