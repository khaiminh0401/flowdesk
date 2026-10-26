import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { forkJoin, map, Observable, timeout } from 'rxjs';

export interface SystemInfo {
  readonly application: string;
  readonly stage: string;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

@Injectable({ providedIn: 'root' })
export class SystemStatusService {
  private readonly http = inject(HttpClient);

  check(): Observable<SystemInfo> {
    return forkJoin({
      info: this.http.get<unknown>('/api/v1/info'),
      health: this.http.get<unknown>('/actuator/health')
    }).pipe(
      timeout(5000),
      map(({ info, health }) => {
        if (!isRecord(info) || typeof info['application'] !== 'string' || !info['application'].trim()
            || typeof info['stage'] !== 'string' || !info['stage'].trim()
            || !isRecord(health) || health['status'] !== 'UP') {
          throw new Error('Invalid or unhealthy system response');
        }
        return { application: info['application'], stage: info['stage'] };
      })
    );
  }
}
