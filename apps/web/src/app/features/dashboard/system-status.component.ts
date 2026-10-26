import { Component, DestroyRef, inject, OnInit, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Subscription } from 'rxjs';
import { SystemInfo, SystemStatusService } from './system-status.service';

type ConnectionState =
  | { kind: 'loading' }
  | { kind: 'ready'; info: SystemInfo }
  | { kind: 'error' };

@Component({
  selector: 'fd-system-status',
  standalone: true,
  template: `
    <section class="connection" aria-labelledby="connection-heading" [attr.aria-busy]="state().kind === 'loading'">
      <h2 id="connection-heading">Application connection</h2>
      @if (state(); as current) {
        @switch (current.kind) {
          @case ('loading') {
            <p role="status">Checking API connection…</p>
          }
          @case ('ready') {
            <p role="status">API connected — {{ current.info.application }} · {{ current.info.stage }}</p>
          }
          @case ('error') {
            <p role="alert">Unable to connect to FlowDesk. Check that the API and database are running, then retry.</p>
          }
        }
        <button type="button" [disabled]="current.kind === 'loading'" (click)="checkConnection()">
          {{ current.kind === 'error' ? 'Retry connection' : 'Check connection' }}
        </button>
      }
    </section>
  `,
  styles: `
    .connection { margin: 0 32px 32px; padding: 24px; background: white; border: 1px solid #e2e8f0; border-radius: 16px; }
    h2 { margin-top: 0; font-size: 1.15rem; }
    p { line-height: 1.6; overflow-wrap: anywhere; }
    button { font: inherit; color: #142235; background: #eef4ff; border: 1px solid #64748b; border-radius: 6px; padding: 10px 16px; cursor: pointer; }
    button:disabled { cursor: wait; opacity: .65; }
    button:focus-visible { outline: 3px solid #2563eb; outline-offset: 3px; }
    @media (max-width: 700px) { .connection { margin: 0 16px 16px; } }
  `
})
export class SystemStatusComponent implements OnInit {
  private readonly service = inject(SystemStatusService);
  private readonly destroyRef = inject(DestroyRef);
  private request?: Subscription;
  readonly state = signal<ConnectionState>({ kind: 'loading' });

  ngOnInit(): void {
    this.checkConnection();
  }

  checkConnection(): void {
    this.request?.unsubscribe();
    this.state.set({ kind: 'loading' });
    this.request = this.service.check().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: info => this.state.set({ kind: 'ready', info }),
      error: () => this.state.set({ kind: 'error' })
    });
  }
}
