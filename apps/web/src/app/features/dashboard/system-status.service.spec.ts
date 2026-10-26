import { provideZonelessChangeDetection } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { SystemStatusService } from './system-status.service';

describe('SystemStatusService', () => {
  let http: HttpTestingController;
  let service: SystemStatusService;
  beforeEach(() => {
    TestBed.configureTestingModule({ providers: [provideZonelessChangeDetection(), provideHttpClient(), provideHttpClientTesting()] });
    http = TestBed.inject(HttpTestingController);
    service = TestBed.inject(SystemStatusService);
  });
  afterEach(() => http.verify());

  it('combines typed info with aggregate health through same-origin GETs', () => {
    const next = jasmine.createSpy('status');
    service.check().subscribe(next);
    const info = http.expectOne('/api/v1/info');
    const health = http.expectOne('/actuator/health');
    expect(info.request.method).toBe('GET');
    expect(health.request.method).toBe('GET');
    info.flush({ application: 'FlowDesk', stage: 'sprint-0', internal: 'must not cross the boundary' });
    expect(next).not.toHaveBeenCalled();
    health.flush({ status: 'UP' });
    expect(next).toHaveBeenCalledOnceWith({ application: 'FlowDesk', stage: 'sprint-0' });
  });

  for (const payload of [{}, null, { application: '', stage: 'sprint-0' }, { application: 'FlowDesk', stage: 1 }]) {
    it(`rejects malformed info: ${JSON.stringify(payload)}`, () => {
      const error = jasmine.createSpy('error');
      service.check().subscribe({ next: () => fail('Invalid info accepted'), error });
      http.expectOne('/api/v1/info').flush(payload);
      http.expectOne('/actuator/health').flush({ status: 'UP' });
      expect(error).toHaveBeenCalled();
    });
  }

  for (const status of ['DOWN', 'OUT_OF_SERVICE', undefined]) {
    it(`rejects unhealthy or malformed health: ${status}`, () => {
      const error = jasmine.createSpy('error');
      service.check().subscribe({ next: () => fail('Invalid health accepted'), error });
      http.expectOne('/api/v1/info').flush({ application: 'FlowDesk', stage: 'sprint-0' });
      http.expectOne('/actuator/health').flush({ status });
      expect(error).toHaveBeenCalled();
    });
  }

  it('bounds an unresponsive check to five seconds and cancels HTTP requests', () => {
    jasmine.clock().install();
    try {
      const error = jasmine.createSpy('timeout');
      service.check().subscribe({ next: () => fail('Unexpected response'), error });
      const info = http.expectOne('/api/v1/info');
      const health = http.expectOne('/actuator/health');
      jasmine.clock().tick(5001);
      expect(error).toHaveBeenCalled();
      expect(info.cancelled).toBeTrue();
      expect(health.cancelled).toBeTrue();
    } finally { jasmine.clock().uninstall(); }
  });
});
