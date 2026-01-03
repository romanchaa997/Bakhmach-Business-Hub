// Event Handlers for Goals + Tasks Microservice
// Implements logic for various domain events

import { eventEmitter, EventMap } from './event-emitter';
import { NotificationService } from '../services/notification.service';
import { CacheService } from '../services/cache.service';
import { GoalRepository } from '../repositories/goal.repository';
import { TaskRepository } from '../repositories/task.repository';

export class EventHandlers {
  private notificationService: NotificationService;
  private cacheService: CacheService;
  private goalRepository: GoalRepository;
  private taskRepository: TaskRepository;

  constructor(
    notificationService: NotificationService,
    cacheService: CacheService,
    goalRepository: GoalRepository,
    taskRepository: TaskRepository
  ) {
    this.notificationService = notificationService;
    this.cacheService = cacheService;
    this.goalRepository = goalRepository;
    this.taskRepository = taskRepository;
  }

  public registerHandlers(): void {
    // Goal Event Handlers
    eventEmitter.on('goal:created', this.handleGoalCreated.bind(this));
    eventEmitter.on('goal:updated', this.handleGoalUpdated.bind(this));
    eventEmitter.on('goal:deleted', this.handleGoalDeleted.bind(this));
    eventEmitter.on('goal:completed', this.handleGoalCompleted.bind(this));

    // Task Event Handlers
    eventEmitter.on('task:created', this.handleTaskCreated.bind(this));
    eventEmitter.on('task:updated', this.handleTaskUpdated.bind(this));
    eventEmitter.on('task:deleted', this.handleTaskDeleted.bind(this));
    eventEmitter.on('task:completed', this.handleTaskCompleted.bind(this));
    eventEmitter.on('task:assigned', this.handleTaskAssigned.bind(this));

    // Notification and Sync Handlers
    eventEmitter.on('notification:sent', this.handleNotificationSent.bind(this));
    eventEmitter.on('sync:triggered', this.handleSyncTriggered.bind(this));
  }

  private async handleGoalCreated(data: EventMap['goal:created']): Promise<void> {
    try {
      // Invalidate goals cache
      await this.cacheService.del(`goals:user:${data.userId}`);
      
      // Send notification
      await this.notificationService.sendNotification(data.userId, {
        type: 'goal_created',
        message: `Goal "${data.title}" has been created`,
        data: { goalId: data.goalId }
      });

      console.log(`[Event Handler] Goal created: ${data.goalId}`);
    } catch (error) {
      console.error('[Event Handler] Error handling goal:created:', error);
    }
  }

  private async handleGoalUpdated(data: EventMap['goal:updated']): Promise<void> {
    try {
      // Invalidate cache
      await this.cacheService.del(`goal:${data.goalId}`);
      
      console.log(`[Event Handler] Goal updated: ${data.goalId}`);
    } catch (error) {
      console.error('[Event Handler] Error handling goal:updated:', error);
    }
  }

  private async handleGoalDeleted(data: EventMap['goal:deleted']): Promise<void> {
    try {
      // Invalidate cache
      await this.cacheService.del(`goal:${data.goalId}`);
      
      console.log(`[Event Handler] Goal deleted: ${data.goalId}`);
    } catch (error) {
      console.error('[Event Handler] Error handling goal:deleted:', error);
    }
  }

  private async handleGoalCompleted(data: EventMap['goal:completed']): Promise<void> {
    try {
      // Update cache
      const goal = await this.goalRepository.findById(data.goalId);
      if (goal) {
        await this.cacheService.set(`goal:${data.goalId}`, goal, 3600);
      }
      
      console.log(`[Event Handler] Goal completed: ${data.goalId}`);
    } catch (error) {
      console.error('[Event Handler] Error handling goal:completed:', error);
    }
  }

  private async handleTaskCreated(data: EventMap['task:created']): Promise<void> {
    try {
      // Invalidate related caches
      await this.cacheService.del(`tasks:goal:${data.goalId}`);
      
      console.log(`[Event Handler] Task created: ${data.taskId}`);
    } catch (error) {
      console.error('[Event Handler] Error handling task:created:', error);
    }
  }

  private async handleTaskUpdated(data: EventMap['task:updated']): Promise<void> {
    try {
      // Invalidate cache
      await this.cacheService.del(`task:${data.taskId}`);
      
      console.log(`[Event Handler] Task updated: ${data.taskId}`);
    } catch (error) {
      console.error('[Event Handler] Error handling task:updated:', error);
    }
  }

  private async handleTaskDeleted(data: EventMap['task:deleted']): Promise<void> {
    try {
      // Invalidate cache
      await this.cacheService.del(`task:${data.taskId}`);
      
      console.log(`[Event Handler] Task deleted: ${data.taskId}`);
    } catch (error) {
      console.error('[Event Handler] Error handling task:deleted:', error);
    }
  }

  private async handleTaskCompleted(data: EventMap['task:completed']): Promise<void> {
    try {
      // Update cache
      const task = await this.taskRepository.findById(data.taskId);
      if (task) {
        await this.cacheService.set(`task:${data.taskId}`, task, 3600);
      }
      
      console.log(`[Event Handler] Task completed: ${data.taskId}`);
    } catch (error) {
      console.error('[Event Handler] Error handling task:completed:', error);
    }
  }

  private async handleTaskAssigned(data: EventMap['task:assigned']): Promise<void> {
    try {
      // Notify assigned user
      await this.notificationService.sendNotification(data.assignedTo, {
        type: 'task_assigned',
        message: `A new task has been assigned to you`,
        data: { taskId: data.taskId }
      });
      
      console.log(`[Event Handler] Task assigned: ${data.taskId} to ${data.assignedTo}`);
    } catch (error) {
      console.error('[Event Handler] Error handling task:assigned:', error);
    }
  }

  private async handleNotificationSent(data: EventMap['notification:sent']): Promise<void> {
    try {
      console.log(`[Event Handler] Notification sent to ${data.userId}: ${data.message}`);
    } catch (error) {
      console.error('[Event Handler] Error handling notification:sent:', error);
    }
  }

  private async handleSyncTriggered(data: EventMap['sync:triggered']): Promise<void> {
    try {
      console.log(`[Event Handler] Sync triggered from ${data.source} at ${data.timestamp}`);
    } catch (error) {
      console.error('[Event Handler] Error handling sync:triggered:', error);
    }
  }
}

export function initializeEventHandlers(
  notificationService: NotificationService,
  cacheService: CacheService,
  goalRepository: GoalRepository,
  taskRepository: TaskRepository
): EventHandlers {
  const handlers = new EventHandlers(
    notificationService,
    cacheService,
    goalRepository,
    taskRepository
  );
  handlers.registerHandlers();
  return handlers;
}
