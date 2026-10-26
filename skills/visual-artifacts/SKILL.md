---
name: visual-artifacts
description: >-
  Úsala SIEMPRE que el usuario pida un artifact: se entrega como HTML visual (generative_ui), NO como
  Markdown. Cubre comparativas, ventajas y desventajas, informes, resúmenes, dashboards, diagramas,
  gráficas, decisiones entre opciones y prototipos de UI, con un método de diseño, componentes y
  ejemplos. Triggers: "artifact", "haz un artifact", "compara", "comparativa", "ventajas y desventajas",
  "informe", "visual", "dashboard", "diagrama", "gráfica", "quiero verlo", "hazlo bonito", "widget".
---

# Visual Artifacts

`generative_ui` explica **cómo** se renderiza un artifact (archivo `.html`, `UserFacing: true`,
`<agent-embed>`, CSP, tokens del host). Esta skill explica **cómo diseñarlo**. Léela antes de
escribir la primera línea de HTML y respeta todas las restricciones de `generative_ui`.

## Restricciones duras (vienen del host, no se negocian)

- Solo se carga un script externo: `https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js`.
  No hay Google Fonts, Chart.js, D3, Mermaid ni iconos por CDN. **Las gráficas y los diagramas se
  hacen con SVG inline** y los iconos también son SVG inline.
- La tipografía la pone el host. La jerarquía sale del tamaño, el peso, el tracking y el color.
- Colores base: usa siempre los tokens del host (`--background`, `--card`, `--foreground`,
  `--muted-foreground`, `--border`, `--primary`, `--accent`...). **No los redefinas en `:root`.**
- El tema claro se detecta con `html.light`. Los colores propios (estados, series de datos) se
  definen en una clase raíz propia con su variante `html.light` (ver
  [design-system.md](./references/design-system.md)).
- No hay texto por debajo de 12px. Nada de `h-screen`, `100vh` ni `height:100%` en el contenedor raíz.

## Flujo

### 1. Decide qué es antes de decidir cómo se ve

Responde en una línea, para ti: *¿qué tiene que entender o decidir el usuario al mirar esto?*
Elige **una** forma:

| Contenido | Forma |
|---|---|
| Un proceso, una arquitectura, un flujo de datos | Diagrama SVG con el mecanismo real |
| Números que cambian o se comparan | KPI + gráfica SVG + tabla de detalle |
| Opciones para elegir | Comparativa en columnas con un veredicto destacado |
| Un cambio de código o un plan | Resumen ejecutivo + pasos con estado + riesgos |
| Un concepto | Explicación en capas: la idea en una frase, un visual y el detalle desplegable |

Si la respuesta cabe en tres líneas de texto, **no hagas un artifact**.

### 2. Fija una dirección visual concreta

Antes de codificar, escribe en un comentario HTML al inicio del archivo:

```html
<!-- dirección: editorial técnico · acento: --primary para la acción, ámbar para riesgo ·
     elemento dominante: diagrama del pipeline · densidad: media -->
```

Prohibido como dirección: "limpio y moderno", "minimalista", "premium". Tienen que ser decisiones
que se puedan comprobar.

### 3. Construye con jerarquía, no con tarjetas iguales

Reglas que separan un artifact visual de uno genérico:

1. **Un elemento dominante.** Una cifra, un diagrama o un veredicto ocupa el doble que lo demás.
   Si todo pesa lo mismo, el usuario no sabe dónde mirar.
2. **Contraste de escala real**: la cifra hero va a 40–56px, las etiquetas a 12–13px en mayúsculas
   con tracking, y el cuerpo a 14–15px. Usa `tabular-nums` para los números.
3. **Ritmo, no padding uniforme**: deja más espacio entre secciones que dentro de ellas.
   Agrupa por proximidad antes de recurrir a bordes.
4. **Composición bento o editorial**: usa columnas de distinto ancho (`grid-cols-[2fr_1fr]`) y
   bloques con `col-span-2`. Evita la rejilla de 3 tarjetas idénticas.
5. **El color tiene significado**: el acento señala acción o foco, y verde, ámbar y rojo indican
   estado. Nunca uses el color como decoración aleatoria.
6. **Profundidad sutil**: superficies con `color-mix` sobre `--card`, sombras suaves en capas y un
   borde de 1px. No uses gradientes chillones ni blobs.
7. **Estados diseñados**: cada elemento interactivo tiene `hover`, `focus-visible` y `active`.
8. **Movimiento con propósito**: una entrada escalonada corta (≤300ms) y nada en bucle, siempre
   dentro de `@media (prefers-reduced-motion: no-preference)`.

Los componentes listos (KPI, badge de estado, tabs, timeline, callout, tabla) están en
[design-system.md](./references/design-system.md). Las recetas de barras, líneas, donut, sparkline
y diagramas de flujo están en [charts-and-diagrams.md](./references/charts-and-diagrams.md).

Antes de escribir, **lee el ejemplo más cercano** y adapta su estructura (no su contenido):

| Si vas a hacer… | Parte de |
|---|---|
| Reporte, métricas, dashboard, resumen de un cambio | [examples/report.html](./examples/report.html) |
| Comparativa de opciones, recomendación, decisión técnica | [examples/decision.html](./examples/decision.html) |
| Explicación de un flujo o arquitectura dentro del chat | [examples/inline-diagram.html](./examples/inline-diagram.html) |

**Widgets inline** (`<agent-embed>`): fondo `bg-transparent`, una sola tarjeta, todo por encima
de 500px de alto. Explica una sola cosa. Si para explicar necesitas más altura, pasa a artifact
standalone. La interacción sustituye a la altura: mejor un nodo que al tocarlo muestra su detalle
que cuatro párrafos apilados.

### 4. Contenido real

- Usa los datos, nombres de archivos y cifras reales de la conversación. Nunca pongas lorem ipsum
  ni "Item 1".
- Los títulos dicen la conclusión ("La latencia bajó 38% tras el cache"), no la categoría
  ("Métricas").
- Las gráficas llevan etiquetas directas sobre las series en lugar de leyenda cuando caben, y
  las unidades van en los ejes.
- **Una cifra, un valor.** Si un dato aparece en el veredicto y en la tabla, debe decir exactamente
  lo mismo. Antes de entregar, busca cada cifra clave en el archivo y unifícala.
- **Mismo conjunto en todas las secciones.** Si la intro dice "cuatro opciones", las cuatro aparecen
  en la matriz, en las tabs y en el veredicto. Si descartas una, dilo explícitamente y quítala de todas.
- **Sin credibilidad inventada.** No pongas "Validado", "datos reales" ni "verificado" salvo que
  tengas fuentes, y entonces cítalas al pie. Si las cifras son estimaciones, dilo en una línea
  ("Cifras estimadas, no auditadas") en `--muted-foreground` al final.

### 5. Verifica antes de entregar

1. Ejecuta el linter. Debe salir sin errores:
   `python3 <ruta-de-esta-skill>/scripts/check_artifact.py <archivo.html>`
2. Toma capturas y detecta desbordes (busca el navegador por su cuenta, no hace falta `chromium`
   en el PATH):
   `python3 <ruta-de-esta-skill>/scripts/screenshot.py <archivo.html>`
   - **Abre los tres PNG que imprime** (escritorio oscuro, escritorio claro y móvil) y míralos de
     verdad antes de seguir.
   - Si dice `DESBORDE`, corrige el elemento culpable (normalmente: `flex-wrap`, `min-w-0`,
     `overflow-x-auto` en su contenedor o `grid-cols-1` en móvil) y vuelve a ejecutarlo hasta que
     diga "Sin desborde".
   - Si sale con código 3 (no hay navegador), usa `scripts/preview.py <archivo.html>` y abre la URL
     `file://` con la herramienta de navegador de Antigravity.
   - Para widgets inline: `preview.py --inline` marca el límite de 500px.
   Las capturas y previews son solo para revisar: se entrega el archivo original.
3. Checklist:
   - [ ] ¿Se entiende el mensaje principal en 3 segundos?
   - [ ] ¿Hay un elemento claramente dominante?
   - [ ] ¿Funciona en tema claro y en tema oscuro (sin colores fijos tipo `text-white`)?
   - [ ] ¿No hay scroll horizontal a 375px?
   - [ ] ¿Cada color significa algo?
   - [ ] ¿Cada cifra repetida dice lo mismo en todas partes y aparecen todas las opciones anunciadas?
   - [ ] ¿Parece diseñado para este contenido o podría ser cualquier plantilla?

Si la última respuesta es "cualquier plantilla", vuelve al paso 2.
