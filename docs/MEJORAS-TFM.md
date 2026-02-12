# Plan de Mejoras - TFM Agenda Escolar Pro

> Documento de seguimiento para verificar requisitos del TFM y cobertura del plan de estudios.
> Fecha de creación: 2026-02-10
> Fecha límite de entrega: 2026-02-23

---

## 1. Requisitos del TFM

Según `docs/Documentacion-TFM.md`:

| # | Requisito | Estado | Notas |
|---|-----------|--------|-------|
| 1 | README.md completo y detallado | ✅ Cumplido | 507 líneas, stack, arquitectura, instalación, funcionalidades |
| 2 | Descripción general del proyecto | ✅ Cumplido | Clara y bien estructurada |
| 3 | Stack tecnológico documentado | ✅ Cumplido | Tabla detallada con versiones |
| 4 | Instalación y ejecución | ✅ Cumplido | Frontend y backend documentados |
| 5 | Estructura del proyecto | ✅ Cumplido | Diagramas Mermaid incluidos |
| 6 | Funcionalidades principales | ✅ Cumplido | Listadas y explicadas |
| 7 | Código en repo público GitHub | ✅ Cumplido | Opción mejor valorada |
| 8 | Despliegue/publicación | ✅ Cumplido | Frontend (Vercel) + Backend (Render) |
| 9 | Slides de presentación | ✅ Cumplido | `Agenda Escolar Pro - Defensa TFM.pptx` creada con Kimi AI |

---

## 2. Cobertura del Plan de Estudios

### 2.1 Temas bien cubiertos

| Tema del Máster | Evidencia en el proyecto |
|-----------------|--------------------------|
| Fundamentos de programación | TypeScript + Python, estructuras de datos, funciones, manejo de errores |
| POO y Paradigmas | Clases Python (modelos, use cases), interfaces TypeScript |
| Git/GitHub | Historial de commits, ramas, repositorio público |
| Ecosistema dev moderno | IDE, terminal, venv, package managers (npm, pip) |
| Clean Architecture | Separación Domain / Application / Infrastructure en backend |
| SOLID y Buenas Prácticas | Dependency Injection (FastAPI Depends), SRP en use cases, repositorios separados |
| Arquitectura de software | Monorepo, Clean Architecture, capas bien definidas |
| APIs y comunicación | REST API completa (~35 endpoints), cliente HTTP con auth |
| Bases de datos | PostgreSQL + SQLAlchemy ORM + Alembic (7 migraciones) |
| IA Generativa | Integración Gemini con 3 funcionalidades AI reales |
| Prompting | Prompts estructurados con restricciones alimentarias, schemas de respuesta JSON |
| Testing | Vitest (frontend, 170 tests, services/utils 100%) + pytest (backend), tests unitarios + integración + E2E Playwright |
| CI/CD | GitHub Actions (2 pipelines), deploy automático a Vercel y Render |
| Cloud computing | Vercel + Render + Supabase (3 servicios cloud distintos) |
| Seguridad (JWT) | Autenticación JWT + bcrypt + Bearer tokens |
| OWASP básico | SQL injection prevenido (ORM), validación inputs (Pydantic), HTTPS, CORS restrictivo |
| Variables de entorno | .env gestionados, .gitignore configurado correctamente |
| DevOps | CI/CD pipelines, linting automatizado, deploy hooks |
| Documentación | README.md extenso, diagramas Mermaid, CLAUDE.md |
| IA en proceso de desarrollo | Uso de Claude Code y GitHub Copilot |
| Code Quality | ESLint, Black, isort, flake8, mypy, TypeScript strict |
| Pre-commit hooks | Husky v9 + lint-staged (frontend) y script shell Black/isort/flake8 (backend) |
| IA responsable | Sección detallada: datos enviados/no enviados, alergias como caso critico, sesgos, transparencia visual |
| Usabilidad | Dark mode, responsive, multi-perfil, módulos activables por hijo |
| Ciclo de vida del software | Diseño → desarrollo → testing → CI/CD → deploy |
| Presentación TFM | `Agenda Escolar Pro - Defensa TFM.pptx` creada con Kimi AI, referenciada en README |
| Test coverage | 170 tests (12 archivos), services/utils al 100%. Umbrales en CI y cobertura documentada en README |

### 2.2 Temas parcialmente cubiertos

| Tema | Estado actual | Mejora propuesta | Prioridad |
|------|--------------|------------------|-----------|
| ~~Pre-commit hooks~~ | ~~Completado~~ | ~~Husky v9 + lint-staged (frontend) + script shell (backend)~~ | ~~Alta~~ |
| Observabilidad (Sentry) | No implementado | Integrar Sentry en frontend y/o backend | Media |
| ~~E2E Testing~~ | ~~Completado~~ | ~~1-2 tests E2E con Playwright~~ | ~~Media~~ |
| ~~Rate limiting~~ | ~~Completado~~ | ~~`slowapi` en FastAPI para endpoints públicos (login/register)~~ | ~~Media~~ |
| ~~IA responsable~~ | ~~Completado~~ | ~~Sección ampliada: datos enviados/no enviados, alergias, sesgos, transparencia~~ | ~~Media~~ |
| ~~Refresh tokens~~ | ~~Completado~~ | ~~Rotación automática con reuse detection, logout endpoint~~ | ~~Baja~~ |

### 2.3 Temas no cubiertos

| Tema del Máster | Relevancia para el proyecto | Acción |
|-----------------|----------------------------|--------|
| ADRs (Architecture Decision Records) | Media - demuestra madurez profesional | Crear 2-3 ADRs con decisiones clave |
| Automatización n8n | Baja - no aplica al proyecto | No implementar |
| LangChain/LlamaIndex | Media - se usa Gemini SDK directo | Válido como está, no requiere cambio |
| Modelos locales (Ollama/LM Studio) | Baja - Gemini cloud es suficiente | No implementar |
| CodeRabbit | Baja - ya hay CI con linting | Opcional: configurar para PRs |

---

## 3. Plan de Acción por Prioridad

### 🟠 Recomendado (alto impacto)

- [x] **~~Corregir configuración CORS~~** *(completado)*

- [x] **~~Configurar pre-commit hooks~~** *(completado)*
  - Frontend: Husky v9 + lint-staged (ESLint --max-warnings 0)
  - Backend: script shell (Black + isort + flake8) sobre archivos staged

- [x] **~~Ampliar sección de IA responsable en README~~** *(completado)*
  - Tabla de datos enviados vs NO enviados a Gemini
  - Alergias como caso critico de seguridad (prompt reforzado, doble barrera, sin garantia absoluta)
  - Limitaciones y sesgos del modelo
  - Transparencia: indicador visual "IA SUGERIDA", estado de carga, prompts auditables

### 🟡 Opcional (diferenciadores)

- [ ] **Integrar Sentry** (observabilidad)
  - Al menos en frontend para capturar errores en producción
  - Demostrar conocimiento de monitoring/observabilidad

- [x] **~~Añadir 1-2 tests E2E con Playwright~~** *(completado)*
  - 3 tests: registro, login, flujo completo (crear perfil → añadir asignatura)
  - Playwright con API mockeada (`page.route()`) para tests deterministas
  - Demuestra conocimiento completo de la pirámide de testing

- [x] **~~Rate limiting en endpoints de auth~~** *(completado)*
  - `slowapi` con límites por IP: login (5/min), register (3/min)
  - Test de integración que verifica HTTP 429 tras superar el límite

- [ ] **Crear 2-3 ADRs**
  - ADR-001: Elección de Clean Architecture para el backend
  - ADR-002: Gemini como proveedor de IA (vs OpenAI, local)
  - ADR-003: Monorepo vs repositorios separados

- [x] **~~Refresh token rotation~~** *(completado)*
  - Token opaco (`secrets.token_urlsafe`) almacenado como hash SHA-256 en BD
  - `POST /auth/refresh`: rota el token (uso único) y emite nuevos access + refresh tokens
  - `POST /auth/logout`: revoca el refresh token para cerrar sesión
  - Reuse detection: token revocado presentado → se invalidan TODAS las sesiones del usuario
  - Expiración configurable (por defecto 7 días) vía `REFRESH_TOKEN_EXPIRE_DAYS`
  - Migración Alembic 008, modelo `RefreshToken`, 10 tests de integración (todos pasan)

---

## 4. Estado del Proyecto (Resumen Técnico)

### Stack desplegado

| Capa | Tecnología | URL |
|------|-----------|-----|
| Frontend | React 19 + TypeScript + Vite + Tailwind | https://agenda-escolar-sage.vercel.app |
| Backend | FastAPI + SQLAlchemy + Alembic | https://agenda-escolar-pnpk.onrender.com |
| Base de datos | PostgreSQL 15 (Supabase) | Conexión privada |
| IA | Google Gemini 3 Flash Preview | API |
| CI/CD | GitHub Actions (2 pipelines) | Automático en push a main |

### Funcionalidades implementadas

- ✅ Registro y login de usuarios (JWT + bcrypt)
- ✅ Gestión multi-hijo (perfiles con alergias y alimentos excluidos)
- ✅ Asignaturas y horarios (escolares y extraescolares)
- ✅ Seguimiento de exámenes
- ✅ Menú escolar por fecha
- ✅ Sugerencia de cenas con IA (individual + semanal)
- ✅ Lista de la compra generada por IA
- ✅ Calendario de eventos (festivos, lectivos, vacaciones)
- ✅ Módulos activables/desactivables por hijo
- ✅ Modo oscuro
- ✅ Diseño responsive (mobile-first)
- ✅ Soft deletes en toda la base de datos
- ✅ Migraciones versionadas (7 versiones Alembic)

### Métricas del código

| Métrica | Valor |
|---------|-------|
| Archivos Python (backend) | ~78 |
| Archivos TypeScript/TSX (frontend) | ~38 |
| Endpoints API | ~35 |
| Migraciones de BD | 7 |
| Pipelines CI/CD | 2 |
| Servicios cloud | 3 (Vercel, Render, Supabase) |

---

## 5. Notas

- La fecha límite del TFM es el **23 de febrero de 2026**
- Todos los requisitos obligatorios están cumplidos (incluidas slides y tests)
- El proyecto ya está desplegado y funcional en producción
- Se recomienda priorizar las mejoras 🟠 antes de la entrega
