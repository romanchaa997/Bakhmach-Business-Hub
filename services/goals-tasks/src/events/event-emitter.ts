// Event Emitter for Goals + Tasks Microservice
// Implements publish-subscribe pattern for event-driven architecture

import { EventEmitter as EE } from 'events';

interface EventListener<T = any> {
  (data: T): void | Promise<void>;
}

interface EventMap {
  'goal:created': { goalId: string; title: string; userId: string };
  'goal:updated': { goalId: string; changes: Record<string, any> };
  'goal:deleted': { goalId: string };
  'goal:completed': { goalId: string; completedAt: Date };
  'task:created': { taskId: string; goalId: string; title: string };
  'task:updated': { taskId: string; changes: Record<string, any> };
  'task:deleted': { taskId: string };
  'task:completed': { taskId: string; completedAt: Date };
  'task:assigned': { taskId: string; assignedTo: string };
  'notification:sent': { userId: string; type: string; message: string };
  'sync:triggered': { source: string; timestamp: Date };
}

export class GoalsTasksEventEmitter {
  private static instance: GoalsTasksEventEmitter;
  private emitter: EE;

  private constructor() {
    this.emitter = new EE();
    this.emitter.setMaxListeners(100);
  }

  public static getInstance(): GoalsTasksEventEmitter {
    if (!GoalsTasksEventEmitter.instance) {
      GoalsTasksEventEmitter.instance = new GoalsTasksEventEmitter();
    }
    return GoalsTasksEventEmitter.instance;
  }

  public on<K extends keyof EventMap>(
    event: K,
    listener: EventListener<EventMap[K]>
  ): void {
    this.emitter.on(event, listener as any);
  }

  public once<K extends keyof EventMap>(
    event: K,
    listener: EventListener<EventMap[K]>
  ): void {
    this.emitter.once(event, listener as any);
  }

  public off<K extends keyof EventMap>(
    event: K,
    listener: EventListener<EventMap[K]>
  ): void {
    this.emitter.off(event, listener as any);
  }

  public emit<K extends keyof EventMap>(
    event: K,
    data: EventMap[K]
  ): boolean {
    return this.emitter.emit(event, data);
  }

  public async emitAsync<K extends keyof EventMap>(
    event: K,
    data: EventMap[K]
  ): Promise<void> {
    const listeners = this.emitter.listeners(event);
    
    for (const listener of listeners) {
      try {
        const result = (listener as any)(data);
        if (result instanceof Promise) {
          await result;
        }
      } catch (error) {
        console.error(`Error in event listener for ${event}:`, error);
      }
    }
  }

  public removeAllListeners<K extends keyof EventMap>(event?: K): void {
    if (event) {
      this.emitter.removeAllListeners(event as any);
    } else {
      this.emitter.removeAllListeners();
    }
  }

  public listenerCount<K extends keyof EventMap>(event: K): number {
    return this.emitter.listenerCount(event as any);
  }

  public getEventNames(): (keyof EventMap)[] {
    return this.emitter.eventNames() as (keyof EventMap)[];
  }
}

export const eventEmitter = GoalsTasksEventEmitter.getInstance();
