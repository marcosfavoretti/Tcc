import { Component, OnInit } from '@angular/core';
import { SplitterModule } from 'primeng/splitter'
import { SideBar } from "../../widgets/side-bar/side-bar";
import { AppPagePlaceHolder } from "../../widgets/app-page-place-holder/app-page-place-holder";
import { GerenciaAlgoritmoResService } from '../../services/GerenciaAlgoritmoRes.service';
import { Map } from "../../widgets/map/map"
import { PickListService } from '../../services/PickList.service';
import { Metricas } from "../../widgets/metricas/metricas";
import { StartUpService } from '../../services/StartUp.service';
import { MapSlider } from "../../widgets/map-slider/map-slider";
@Component({
  selector: 'app-app-page',
  imports: [Map, SplitterModule, SideBar, AppPagePlaceHolder, Metricas, MapSlider],
  templateUrl: './app-page.html',
  styleUrl: './app-page.css'
})
export class AppPage implements OnInit{
  constructor(
    private startUpService: StartUpService,
    public pickListService: PickListService,
    public gerenciaAlgoritmoResService: GerenciaAlgoritmoResService
  ) { }

  ngOnInit(): void {
    this.startUpService.startUp();
  }
}
