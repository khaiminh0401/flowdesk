import { Component } from '@angular/core';
import { SystemStatusComponent } from './system-status.component';

@Component({
  selector: 'fd-dashboard',
  standalone: true,
  imports: [SystemStatusComponent],
  template: `
    <section class="welcome">
      <h2>Build reliable workflows.</h2>
      <p>FlowDesk is under active development. Workspace, projects, tasks and approvals are upcoming milestones.</p>
    </section>
    <fd-system-status />
  `
})
export class DashboardComponent {}
