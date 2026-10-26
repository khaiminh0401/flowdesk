import { TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { provideRouter, Router } from '@angular/router';
import { AppComponent } from './app.component';
import { routes } from './app.routes';

describe('Application shell', () => {
  beforeEach(() => TestBed.configureTestingModule({
    imports: [AppComponent],
    providers: [provideZonelessChangeDetection(), provideRouter(routes)]
  }));

  it('provides a named navigation landmark and a skip link to main content', async () => {
    const fixture = TestBed.createComponent(AppComponent);
    await fixture.whenStable();
    const element: HTMLElement = fixture.nativeElement;
    expect(element.querySelector('nav')?.getAttribute('aria-label')).toBe('Primary');
    const skip = element.querySelector<HTMLAnchorElement>('a[href="#main-content"]');
    expect(skip).not.toBeNull();
    expect(element.querySelector('main')?.id).toBe('main-content');
  });

  it('renders the lazy dashboard and marks its navigation link as current', async () => {
    const fixture = TestBed.createComponent(AppComponent);
    await TestBed.inject(Router).navigateByUrl('/');
    await fixture.whenStable();
    const element: HTMLElement = fixture.nativeElement;
    expect(element.querySelector('main h2')?.textContent).toContain('Build reliable workflows.');
    expect(element.querySelector('nav a')?.getAttribute('aria-current')).toBe('page');
  });

  it('redirects unknown URLs to the dashboard', async () => {
    const fixture = TestBed.createComponent(AppComponent);
    const router = TestBed.inject(Router);
    await router.navigateByUrl('/not-a-page');
    await fixture.whenStable();
    expect(router.url).toBe('/');
    expect(fixture.nativeElement.querySelector('fd-dashboard')).not.toBeNull();
  });
});
