/**
 * Application-wide constants
 */

// Project status severity mapping for PrimeVue Tags
export const STATUS_SEVERITY = {
  created: 'info',
  running: 'success',
  stopped: 'warning',
  error: 'danger'
}

// Toast notification durations (ms)
export const TOAST_DURATION = {
  SHORT: 2000,
  NORMAL: 3000,
  LONG: 5000
}

// Toast severity types
export const TOAST_SEVERITY = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARN: 'warn',
  INFO: 'info'
}

// Project statuses
export const PROJECT_STATUS = {
  CREATED: 'created',
  RUNNING: 'running',
  STOPPED: 'stopped',
  ERROR: 'error'
}

// API error messages
export const ERROR_MESSAGES = {
  LOAD_PROJECTS_FAILED: 'Failed to load projects',
  DELETE_PROJECT_FAILED: 'Failed to delete project',
  START_CONTAINER_FAILED: 'Failed to start container',
  STOP_CONTAINER_FAILED: 'Failed to stop container',
  RESTART_CONTAINER_FAILED: 'Failed to restart container',
  LOAD_PRESETS_FAILED: 'Failed to load presets',
  SAVE_PROJECT_FAILED: 'Failed to save project',
  VALIDATION_ERROR: 'Please fill all required fields'
}

// Success messages
export const SUCCESS_MESSAGES = {
  PROJECT_CREATED: 'Project created successfully',
  PROJECT_UPDATED: 'Project updated successfully',
  PROJECT_DELETED: 'Project deleted successfully',
  CONTAINER_STARTED: 'Container started successfully',
  CONTAINER_STOPPED: 'Container stopped successfully',
  CONTAINER_RESTARTED: 'Container restarted successfully',
  ENV_VARS_UPDATED: 'Environment variables updated successfully'
}

