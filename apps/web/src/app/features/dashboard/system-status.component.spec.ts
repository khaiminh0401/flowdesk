import { provideZonelessChangeDetection } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SystemStatusComponent } from './system-status.component';

describe('Dashboard API connection', () => {
  let fixture: ComponentFixture<SystemStatusComponent>;
  let http: HttpTestingController;
  let element: HTMLElement;
  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [SystemStatusComponent],
      providers: [provideZonelessChangeDetection(), provideHttpClient(), provideHttpClientTesting()]
    });
    fixture = TestBed.createComponent(SystemStatusComponent);
    http = TestBed.inject(HttpTestingController);
    element = fixture.nativeElement;
    fixture.detectChanges();
  });
  afterEach(() => http.verify());

  function healthy() {
    http.expectOne('/api/v1/info').flush({ application: 'FlowDesk', stage: 'sprint-0' });
    http.expectOne('/actuator/health').flush({ status: 'UP' });
    fixture.detectChanges();
  }

  it('announces loading and prevents duplicate checks until both requests finish', () => {
    expect(element.querySelector('section')?.getAttribute('aria-busy')).toBe('true');
    expect(element.querySelector('[role="status"]')?.textContent).toContain('Checking API connection');
    expect(element.querySelector('button')?.disabled).toBeTrue();
    healthy();
    expect(element.textContent).toContain('API connected');
    expect(element.textContent).toContain('FlowDesk');
    expect(element.textContent).toContain('sprint-0');
    expect(element.querySelector('section')?.getAttribute('aria-busy')).toBe('false');
  });

  it('clears old success while checking again', () => {
    healthy();
    element.querySelector('button')?.click();
    fixture.detectChanges();
    expect(element.textContent).not.toContain('API connected');
    expect(element.querySelector('button')?.disabled).toBeTrue();
    healthy();
  });

  it('hides raw server errors and retries successfully after an HTTP failure', () => {
    const info = http.expectOne('/api/v1/info');
    const health = http.expectOne('/actuator/health');
    info.flush('private stack trace and password', { status: 500, statusText: 'Internal Server Error' });
    fixture.detectChanges();
    expect(health.cancelled).toBeTrue();
    expect(element.querySelector('[role="alert"]')?.textContent).toContain('Unable to connect');
    expect(element.textContent).not.toContain('private stack trace');
    expect(element.querySelector('button')?.textContent).toContain('Retry connection');
    element.querySelector('button')?.click();
    fixture.detectChanges();
    healthy();
    expect(element.querySelector('[role="alert"]')).toBeNull();
    expect(element.textContent).toContain('API connected');
  });

  it('shows a safe retryable error on network failure', () => {
    const info = http.expectOne('/api/v1/info');
    const health = http.expectOne('/actuator/health');
    info.error(new ProgressEvent('error'));
    fixture.detectChanges();
    expect(health.cancelled).toBeTrue();
    expect(element.querySelector('[role="alert"]')).not.toBeNull();
    expect(element.querySelector('button')?.disabled).toBeFalse();
  });

  it('cancels both requests when the component is destroyed', () => {
    const info = http.expectOne('/api/v1/info');
    const health = http.expectOne('/actuator/health');
    fixture.destroy();
    expect(info.cancelled).toBeTrue();
    expect(health.cancelled).toBeTrue();
  });
});
