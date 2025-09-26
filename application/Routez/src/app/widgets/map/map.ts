import { AfterViewInit, Component, ElementRef, EventEmitter, Input, Output, viewChild } from '@angular/core';
import * as L from 'leaflet';
import { PontoDTO } from '../../../api';
import { PontoDtoCor } from '../../@core/types/PontoDtoCor';

@Component({
  selector: 'app-map',
  // Assumindo que a configuração de standalone/módulos está no seu projeto
  imports: [], 
  templateUrl: './map.html',
  styleUrl: './map.css'
})
export class Map implements AfterViewInit {
  private map!: L.Map;
  public selectedPoint!: Partial<PontoDTO>;
  @Input() selectable: boolean = true;
  @Input() ruas: L.LatLngExpression[] = [];
  @Input() preSelectPoint: PontoDtoCor[] = [];
  @Output() onSelectPoint: EventEmitter<Partial<PontoDTO>> = new EventEmitter();
  mapInstance = viewChild<ElementRef>('mapInstance');
  private currentMarker: L.Marker | null = null;

  // NOVO: Método público para forçar o Leaflet a redimensionar
  public resizeMap(): void {
    if (this.map) {
      // Utilizamos setTimeout(0) para garantir que o redimensionamento ocorra
      // após o browser ter finalizado o cálculo de layout do container flex.
      setTimeout(() => {
        this.map.invalidateSize();
        // Opcional: Centralizar o mapa novamente para garantir o foco correto.
        this.map.setView(this.map.getCenter(), this.map.getZoom());
      }, 0);
    }
  }

  loadPoints(): void {
    this.preSelectPoint.forEach(
      point =>
        L.marker([point.latitude, point.longitude], {
          icon: this.criarMarcadorComPrimeIcon('pi pi-map-marker', point.cor)
        })
          .addTo(this.map)
          .bindPopup(`Nome:${point.name.toLocaleLowerCase()}<br>Latitude: ${point.latitude.toFixed(5)}<br>Longitude: ${point.longitude.toFixed(5)}`)
          .openPopup()
    )
  }

  criarMarcadorComPrimeIcon(iconClass: string, cor: string): L.DivIcon {
    return L.divIcon({
      className: '', 
      html: `
        <i class="${iconClass}" style="color: ${cor}; font-size: 30px;"></i>
      `,
      iconSize: [30, 30],     
      iconAnchor: [15, 30],   
    });
  }

  ngAfterViewInit(): void {
    this.initMap();
    this.loadPoints();
    this.desenharRuas();
  }

  private initMap(): void {
    const boituvaBounds = L.latLngBounds(
      [-23.31, -47.705],  
      [-23.25, -47.615]   
    );
    
    const mapElement = this.mapInstance();
    if (!mapElement) {
        console.error('Elemento container do mapa não encontrado!');
        return;
    }

    this.map = L.map(mapElement.nativeElement, {
      center: [-23.2822, -47.6715], 
      zoom: 14,
      minZoom: 13,
      maxZoom: 17,
      maxBounds: boituvaBounds,
      maxBoundsViscosity: 1.0, 
      zoomControl: true,
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(this.map);

    this.map.on('click', (e: L.LeafletMouseEvent) => {
      if (boituvaBounds.contains(e.latlng)) {
        const { lat, lng } = e.latlng;
        if (this.currentMarker) {
          this.map.removeLayer(this.currentMarker);
        }

        this.selectable && (
          this.currentMarker = L.marker([lat, lng], {
            icon: this.criarMarcadorComPrimeIcon('pi pi-map-marker', 'black')
          })
            .addTo(this.map)
            .bindPopup(`Lat: ${lat.toFixed(5)}<br>Lng: ${lng.toFixed(5)}`)
            .openPopup()
        );

        this.onSelectPoint.emit({
          latitude: lat,
          longitude: lng
        })
      };
    });
  }
  private desenharRuas(): void {
    if (!this.ruas?.length) return;
    L.polyline(this.ruas, {
      color: 'blue',
      weight: 5
    })
      .addTo(this.map);
  }
}
