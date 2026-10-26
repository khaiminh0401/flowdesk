import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

@Component({
  selector: 'fd-root',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  template: `
    <a class="skip-link" href="#main-content">Skip to main content</a>
    <div class="shell">
      <aside><h1>FlowDesk</h1><nav aria-label="Primary"><a routerLink="/" routerLinkActive="active" ariaCurrentWhenActive="page" [routerLinkActiveOptions]="{ exact: true }">Dashboard</a></nav></aside>
      <main id="main-content" tabindex="-1"><header>Enterprise Workspace <span>Sprint 0</span></header><router-outlet /></main>
    </div>
  `
})
export class AppComponent {}
