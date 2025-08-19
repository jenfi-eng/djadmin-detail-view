# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is `djadmin-detail-view`, a Django package that adds missing DetailView functionality to Django Admin. It allows creation of read-only detail views for objects in Django Admin using a DSL approach inspired by Rails' ActiveAdmin.

## Development Commands

### Python/Django Commands
- **Install dependencies**: `poetry install`
- **Run development server**: `python server.py` (uses uvicorn with SSL and auto-reload)
- **Run tests**: `pytest` (configured in pyproject.toml with `--ds=example_project.settings_test`)
- **Run single test**: `pytest path/to/test_file.py::test_function_name`
- **Django management**: `python manage.py <command>` (uses example_project.settings)

### Frontend/Webpack Commands
- **Development server**: `npm run dev` (webpack dev server)
- **Production build**: `npm run build`
- **Test build**: `npm run build_test`

### Code Quality
- **Linting**: `ruff check` (configured in pyproject.toml)
- **Type checking**: `mypy` (configured in pyproject.toml)
- **Template linting**: Uses djLint for Django templates

## Architecture

### Core Components

**Main Package (`djadmin_detail_view/`)**:
- `mixins.py`: Contains `AdminChangeListViewDetail` and `AdminDetailMixin` classes
  - `AdminChangeListViewDetail`: Mixin for ModelAdmin to add "View" buttons and detail URL routing
  - `AdminDetailMixin`: Mixin for DetailView to integrate with Django Admin interface
- `template_helpers.py`: DSL functions for building detail views
  - `details_table_for()`: Creates detail tables for single objects
  - `table_for()`: Creates list tables for related objects
  - `detail()/col()`: Column definitions with auto-formatting
- `url_helpers.py`: Admin URL generation utilities
- `templatetags/djadmin_tags.py`: Custom template tags

**Templates (`djadmin_detail_view/templates/admin/djadmin_components/`)**:
- `auto_layout_detail.html`: Main detail view template
- `object_details.html`, `object_list.html`: Component templates
- `_auto_*.html`: Sub-component templates

### Integration Pattern

1. Add `AdminChangeListViewDetail` mixin to existing ModelAdmin
2. Create DetailView class inheriting from `AdminDetailMixin` and Django's `DetailView`
3. Implement `get_default_detail_view()` method in ModelAdmin
4. Use DSL in DetailView's `get_context_data()` to define layout structure

### Example Project Structure

The `example_project/` demonstrates usage with Company/Contact models and includes:
- Complete Django project setup with webpack integration
- SSL development server configuration
- Bootstrap 5 frontend with Stimulus controllers
- Playwright tests for end-to-end testing

## Dependencies & Requirements

- **Python**: 3.11+
- **Django**: 4.0+
- **Node.js**: 18
- **Frontend**: Bootstrap 5, Stimulus, webpack
- **Required**: django-webpack-loader for asset integration
- **Development**: Poetry for Python dependencies, yarn/npm for frontend

## Testing

- Uses pytest with django plugin
- Test settings in `example_project/settings_test.py`
- Playwright for browser testing
- Factory Boy for test data generation

## Notes

- This package has Jenfi-specific dependencies that may need abstraction for general use
- SSL certificates in `docker/support/` for local HTTPS development
- Uses webpack for frontend asset compilation with django-webpack-loader integration
- Template formatting uses djLint with Django profile
