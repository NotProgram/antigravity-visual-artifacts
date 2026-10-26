---
trigger: always_on
glob:
description: Los artifacts que el usuario va a leer se entregan como HTML visual, no como Markdown.
---

# Artifacts visuales: HTML por defecto

Cuando el usuario pida un **artifact**, una **comparativa**, un **informe**, un **resumen**, un
**dashboard**, un **diagrama**, ventajas y desventajas, o diga que quiere **"verlo"**, entrégalo como
artifact **HTML** (skill `generative_ui`), **no como un archivo `.md`**. Esto aplica aunque el
contenido sea mayormente texto: una comparativa de 3 opciones es una página con veredicto y tabla,
no un documento.

Antes de escribir el HTML:

1. Lee la skill `generative_ui` (mecánica: archivo `.html`, `UserFacing: true`, CSP, tokens).
2. Lee **completa** (todas las líneas, no solo las primeras 100) la skill de diseño:
   `{{SKILL_MD}}`
3. Lee el ejemplo que su tabla indique para ese tipo de contenido y sigue su paso 5 de verificación.

Markdown solo para: implementation plan, task list y walkthrough del propio flujo de trabajo, o
cuando el usuario pida explícitamente Markdown, un `.md` o un documento de texto. Si dudas entre
Markdown y HTML para algo que el usuario va a leer para entender o decidir, elige HTML.
