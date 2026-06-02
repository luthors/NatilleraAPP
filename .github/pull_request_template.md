## Descripción
<!-- Qué cambió y por qué. Sé conciso pero completo. -->

## Issues cerrados
Closes #<!-- número del issue / ISSUE-XX de ISSUES.md -->

## Tipo de cambio
- [ ] `feat` — nueva funcionalidad
- [ ] `fix` — corrección de bug
- [ ] `refactor` — sin nueva funcionalidad ni fix
- [ ] `docs` — solo documentación
- [ ] `test` — tests nuevos o corregidos
- [ ] `chore` — mantenimiento (deps, config)

## Sub-proyecto
- [ ] `backend/`
- [ ] `frontend/`
- [ ] `mobile/`

## Checklist
- [ ] El título del PR sigue Conventional Commits (`tipo(scope): descripción`)
- [ ] El código sigue las convenciones del proyecto (ver `AGENTS.md`)
- [ ] Se probó localmente sin errores (`pytest` / `npm test` / `expo start`)
- [ ] No se incluyen archivos `.env`, `node_modules`, `__pycache__`
- [ ] Si hay nuevos endpoints, el Swagger `/docs` los muestra correctamente
- [ ] Se actualizó documentación relevante (`ISSUES.md`, `docs/traceability/`) si aplica
