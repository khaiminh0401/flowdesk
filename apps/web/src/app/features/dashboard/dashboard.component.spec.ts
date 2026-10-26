import { TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { DashboardComponent } from './dashboard.component';

describe('Dashboard foundation', () => {
  it('explains the empty workspace without advertising available business actions', async () => {
    TestBed.configureTestingModule({providers: [provideZonelessChangeDetection()]});
    const fixture = TestBed.createComponent(DashboardComponent);
    await fixture.whenStable();
    const element: HTMLElement = fixture.nativeElement;
    expect(element.querySelector('h2')?.textContent).toContain('Build reliable workflows.');
    expect(element.querySelector('p')?.textContent).toContain('under active development');
    expect(element.querySelector('p')?.textContent).toContain('upcoming milestones');
    expect(element.querySelector('button, a')).toBeNull();
  });
});
