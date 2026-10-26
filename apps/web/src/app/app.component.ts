import { Component } from '@angular/core';
import { RouterLink, RouterOutlet } from '@angular/router';

@Component({
  selector: 'fd-root',
  standalone: true,
  imports: [RouterLink, RouterOutlet],
  template: `
    <div class="shell">
      <aside><h1>FlowDesk</h1><nav><a routerLink="/">Dashboard</a></nav></aside>
      <main><header>Enterprise Workspace <span>Sprint 0</span></header><router-outlet /></main>
    </div>
  `
})
export class AppComponent {}
