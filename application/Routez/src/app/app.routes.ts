import { Routes } from '@angular/router';
import { AppPage } from './pages/app-page/app-page';

export const routes: Routes = [

    {
        path: "", pathMatch: 'full', redirectTo: 'app'
    },
    {
        path: 'app', component: AppPage
    }
];
