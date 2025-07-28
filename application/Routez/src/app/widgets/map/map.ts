import { AfterViewInit, Component, ElementRef, EventEmitter, Input, OnChanges, OnInit, Output, viewChild, ViewChild } from '@angular/core';
import * as L from 'leaflet';
import { PontoDTO } from '../../../api';

@Component({
  selector: 'app-map',
  imports: [],
  templateUrl: './map.html',
  styleUrl: './map.css'
})
export class Map implements AfterViewInit {
  private map!: L.Map;
  public selectedPoint!: Partial<PontoDTO>;
  @Input() selectable: boolean = true;
  @Input() ruas: string[] = [];
  @Input() preSelectPoint: PontoDTO[] = [];
  @Output() onSelectPoint: EventEmitter<Partial<PontoDTO>> = new EventEmitter();
  mapInstance = viewChild<ElementRef>('mapInstance');
  private currentMarker: L.Marker | null = null;


  loadPoints(): void {
    this.preSelectPoint.forEach(
      point =>
        L.marker([point.latitude, point.longitude])
          .addTo(this.map)
          .bindPopup(`Nome:${point.name.toLocaleLowerCase()}<br>Latitude: ${point.latitude.toFixed(5)}<br>Longitude: ${point.longitude.toFixed(5)}`)
          .openPopup()
    )
  }

  ngAfterViewInit(): void {
    this.initMap();
    this.loadPoints();
    this.desenharRuas();
  }

  private initMap(): void {
    // Coordenadas que limitam Boituva-SP
    const boituvaBounds = L.latLngBounds(
      [-23.31, -47.705],  // sudoeste
      [-23.25, -47.615]   // nordeste
    );

    this.map = L.map(this.mapInstance()?.nativeElement, {
      center: [-23.2822, -47.6715], // Centro da cidade
      zoom: 14,
      minZoom: 13,
      maxZoom: 17,
      maxBounds: boituvaBounds,
      maxBoundsViscosity: 1.0, // Impede arrastar para fora
      zoomControl: true,

    });

    // Camada do mapa
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(this.map);

    // Clique para selecionar ponto (apenas se estiver dentro dos limites)
    this.map.on('click', (e: L.LeafletMouseEvent) => {
      if (boituvaBounds.contains(e.latlng)) {
        const { lat, lng } = e.latlng;
        if (this.currentMarker) {
          this.map.removeLayer(this.currentMarker);
        }

        this.selectable && (
          this.currentMarker = L.marker([lat, lng])
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
  private desenharRua(nomeRua: string): void {
    const query = `
    [out:json];
    way(${nomeRua});
    (._;>;);
    out body;
  `;

    fetch(`https://overpass-api.de/api/interpreter`, {
      method: 'POST',
      body: query,
    })
      .then(res => res.json())
      .then(data => {
        console.log('Dados recebidos:', data);

        const nodes: Record<string, [number, number]> = {};
        data.elements.forEach((el: any) => {
          if (el.type === 'node') {
            nodes[el.id] = [el.lat, el.lon];
          }
        });

        const ways = data.elements.filter((el: any) => el.type === 'way');

        ways.forEach((way: any) => {
          const coords = way.nodes.map((nodeId: number) => nodes[nodeId]).filter(Boolean);
          if (coords.length > 1) {
            L.polyline(coords, {
              color: 'blue',
              weight: 4,
              opacity: 0.8
            }).addTo(this.map);
          }
        });
      })
      .catch(err => console.error(`Erro ao carregar rua "${nomeRua}":`, err));
  }
  private desenharRuas(): void {
    if (!this.ruas?.length) return;

    for (const nomeRua of this.ruas) {
      console.log(nomeRua)
      this.desenharRua(nomeRua);
    }
  }
}
