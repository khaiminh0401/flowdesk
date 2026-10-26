import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { DashboardComponent } from './dashboard.component';

describe('Dashboard foundation', () => {
  it('explains the empty workspace without advertising available business actions', async () => {
    TestBed.configureTestingModule({providers: [provideZonelessChangeDetection(), provideHttpClient(), provideHttpClientTesting()]});
    const fixture = TestBed.createComponent(DashboardComponent);
    fixture.detectChanges();
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('/api/v1/info').flush({ application: 'FlowDesk', stage: 'sprint-0' });
    http.expectOne('/actuator/health').flush({ status: 'UP' });
    await fixture.whenStable();
    http.verify();
    const element: HTMLElement = fixture.nativeElement;
    expect(element.querySelector('h2')?.textContent).toContain('Build reliable workflows.');
    expect(element.querySelector('p')?.textContent).toContain('under active development');
    expect(element.querySelector('p')?.textContent).toContain('upcoming milestones');
    expect(element.querySelector('.welcome button, .welcome a')).toBeNull();
  });
});
