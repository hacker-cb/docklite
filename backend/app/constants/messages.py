"""
API response messages
"""


class ErrorMessages:
    """Error messages for API responses"""

    # Authentication
    INVALID_CREDENTIALS = "Invalid username or password"
    INACTIVE_USER = "User account is inactive"
    INVALID_TOKEN = "Invalid or expired token"

    # Projects
    PROJECT_NOT_FOUND = "Project not found"
    PROJECT_EXISTS = "Project with this domain already exists"
    INVALID_COMPOSE = "Invalid docker-compose.yml content"

    # Users
    USER_NOT_FOUND = "User not found"
    USERNAME_EXISTS = "Username already exists"
    EMAIL_EXISTS = "Email already exists"
    CANNOT_MODIFY_SELF = "Cannot modify your own account"
    CANNOT_DELETE_SELF = "Cannot delete your own account"
    PASSWORD_TOO_SHORT = "Password must be at least 6 characters"

    # Containers
    CONTAINER_START_FAILED = "Failed to start container"
    CONTAINER_STOP_FAILED = "Failed to stop container"
    CONTAINER_RESTART_FAILED = "Failed to restart container"

    # Permissions
    ADMIN_REQUIRED = "Admin access required"
    AUTHENTICATION_REQUIRED = "Authentication required"

    # Setup
    SETUP_ALREADY_DONE = "Setup has already been completed"
    SETUP_REQUIRED = "Initial setup is required"

    # Validation
    VALIDATION_ERROR = "Validation error"
    REQUIRED_FIELD = "This field is required"


class SuccessMessages:
    """Success messages for API responses"""

    # Projects
    PROJECT_CREATED = "Project created successfully"
    PROJECT_UPDATED = "Project updated successfully"
    PROJECT_DELETED = "Project deleted successfully"

    # Users
    USER_CREATED = "User created successfully"
    USER_UPDATED = "User updated successfully"
    USER_DELETED = "User deleted successfully"
    PASSWORD_CHANGED = "Password changed successfully"

    # Containers
    CONTAINER_STARTED = "Container started successfully"
    CONTAINER_STOPPED = "Container stopped successfully"
    CONTAINER_RESTARTED = "Container restarted successfully"

    # Auth
    LOGIN_SUCCESS = "Login successful"
    LOGOUT_SUCCESS = "Logout successful"
    SETUP_SUCCESS = "Setup completed successfully"

    # Environment
    ENV_VARS_UPDATED = "Environment variables updated successfully"
