# Sistema de diseño para artifacts

Copia el bloque `<style>` base en el `<head>` y luego usa los componentes que necesites. Todo cuelga
de la clase `.va`, que va en `<body>`, así que nunca se tocan los tokens del host en `:root`.

## Bloque base (obligatorio)

```html
<style>
  .va {
    /* estados (tema oscuro por defecto; el host marca el claro con html.light) */
    --va-ok:   oklch(74% 0.15 155);
    --va-warn: oklch(80% 0.15 75);
    --va-bad:  oklch(70% 0.19 25);
    --va-info: var(--primary);
    /* series categóricas para gráficas: en este orden, máximo 5 */
    --va-s1: var(--primary);
    --va-s2: oklch(75% 0.13 195);
    --va-s3: oklch(80% 0.14 85);
    --va-s4: oklch(70% 0.16 330);
    --va-s5: oklch(72% 0.12 145);
    /* superficies derivadas de los tokens del host */
    /* mezclas de neutros en srgb: en oklch dos grises pueden dar un tinte de color espurio */
    --va-raised: color-mix(in srgb, var(--foreground) 4%, var(--card));
    --va-sunken: color-mix(in srgb, var(--foreground) 5%, var(--background));
    --va-hairline: color-mix(in srgb, var(--border) 70%, transparent);
    --va-shadow: 0 1px 2px rgb(0 0 0 / .25), 0 12px 32px -16px rgb(0 0 0 / .55);
    --va-radius-lg: 16px;
    --va-radius-sm: 8px;
    --va-ease: cubic-bezier(.16, 1, .3, 1);
  }
  html.light .va {
    --va-ok:   oklch(52% 0.14 155);
    --va-warn: oklch(58% 0.15 65);
    --va-bad:  oklch(53% 0.2 25);
    --va-s2: oklch(55% 0.12 210);
    --va-s3: oklch(62% 0.15 70);
    --va-s4: oklch(55% 0.18 330);
    --va-s5: oklch(55% 0.13 150);
    --va-shadow: 0 1px 2px rgb(15 23 42 / .06), 0 12px 32px -18px rgb(15 23 42 / .25);
  }

  .va { font-variant-numeric: tabular-nums; -webkit-font-smoothing: antialiased; }
  .va-label { font-size: 12px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase;
              color: var(--muted-foreground); }
  .va-hero  { font-size: clamp(40px, 6vw, 56px); font-weight: 700; line-height: 1;
              letter-spacing: -.03em; }
  .va-title { font-size: clamp(22px, 3vw, 28px); font-weight: 650; letter-spacing: -.02em;
              line-height: 1.15; text-wrap: balance; }
  .va-body  { font-size: 15px; line-height: 1.6; color: var(--muted-foreground); text-wrap: pretty; }

  .va-panel { background: var(--card); border: 1px solid var(--va-hairline);
              border-radius: var(--va-radius-lg); box-shadow: var(--va-shadow); }
  .va-well  { background: var(--va-sunken); border-radius: var(--va-radius-sm); }

  @media (prefers-reduced-motion: no-preference) {
    .va-rise { animation: va-rise .45s var(--va-ease) both; animation-delay: calc(var(--i, 0) * 60ms); }
    @keyframes va-rise { from { opacity: 0; transform: translateY(8px); } }
  }
</style>
```

Uso: `<body class="va bg-[var(--background)] text-[var(--foreground)] p-6 md:p-10">` para un
artifact standalone, o `bg-transparent` si va inline. Añade `va-rise` con `style="--i:2"` a los
bloques principales para la entrada escalonada.

## Jerarquía de un layout típico

```html
<main class="mx-auto max-w-5xl space-y-10">
  <header class="space-y-3 va-rise">
    <p class="va-label">Rendimiento · semana 43</p>
    <h1 class="va-title">La latencia p95 bajó 38% tras activar el cache</h1>
    <p class="va-body max-w-2xl">Una frase de contexto que explica el porqué.</p>
  </header>

  <!-- bento: una pieza dominante + una columna secundaria -->
  <section class="grid gap-4 md:grid-cols-[2fr_1fr]">
    <article class="va-panel p-6 va-rise" style="--i:1">…gráfica principal…</article>
    <div class="grid gap-4">
      <article class="va-panel p-5 va-rise" style="--i:2">…KPI…</article>
      <article class="va-panel p-5 va-rise" style="--i:3">…KPI…</article>
    </div>
  </section>
</main>
```

El espacio entre secciones (`space-y-10`) es mayor que el espacio dentro de ellas (`gap-4`). Ese
contraste es el ritmo.

## Componentes

### KPI con delta

```html
<div class="space-y-2">
  <p class="va-label">Latencia p95</p>
  <p class="va-hero">212<span class="text-2xl font-semibold text-[var(--muted-foreground)]">ms</span></p>
  <p class="text-sm"><span class="va-badge is-ok">▼ 38%</span>
     <span class="text-[var(--muted-foreground)]"> vs. semana 42</span></p>
</div>
```

### Badge de estado

```html
<style>
  .va-badge { --tone: var(--va-info); display: inline-flex; align-items: center; gap: .35em;
    padding: 2px 8px; border-radius: 999px; font-size: 12px; font-weight: 600;
    color: var(--tone); background: color-mix(in oklch, var(--tone) 14%, transparent);
    border: 1px solid color-mix(in oklch, var(--tone) 28%, transparent); }
  .va-badge.is-ok   { --tone: var(--va-ok); }
  .va-badge.is-warn { --tone: var(--va-warn); }
  .va-badge.is-bad  { --tone: var(--va-bad); }
</style>
<span class="va-badge is-warn">● En revisión</span>
```

### Callout (riesgo, nota, decisión)

```html
<style>
  .va-callout { --tone: var(--va-info); border-left: 3px solid var(--tone);
    background: color-mix(in oklch, var(--tone) 8%, var(--card));
    border-radius: 0 var(--va-radius-sm) var(--va-radius-sm) 0; padding: 14px 16px; }
</style>
<aside class="va-callout" style="--tone: var(--va-warn)">
  <p class="font-semibold">Riesgo: la migración bloquea la tabla 4 min</p>
  <p class="va-body text-sm">Ejecutar fuera de horario o usar <code>CONCURRENTLY</code>.</p>
</aside>
```

### Tabs accesibles

```html
<style>
  /* con 4+ tabs en móvil la fila hace scroll dentro de sí misma en vez de desbordar la página */
  .va-tabs { display: flex; width: fit-content; max-width: 100%; overflow-x: auto; scrollbar-width: none;
    gap: 2px; padding: 3px; border-radius: 10px; background: var(--va-sunken); }
  .va-tab { flex: none; white-space: nowrap; padding: 6px 12px; border-radius: 8px; font-size: 13px; font-weight: 550;
    color: var(--muted-foreground); transition: background .15s, color .15s; }
  .va-tab:hover { color: var(--foreground); }
  .va-tab[aria-selected="true"] { background: var(--card); color: var(--foreground); box-shadow: var(--va-shadow); }
  .va-tab:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }
</style>
<div class="va-tabs" role="tablist">
  <button class="va-tab" role="tab" aria-selected="true" aria-controls="p1">Resumen</button>
  <button class="va-tab" role="tab" aria-selected="false" aria-controls="p2" tabindex="-1">Detalle</button>
</div>
<section id="p1" role="tabpanel">…</section>
<section id="p2" role="tabpanel" hidden>…</section>
<script>
  document.querySelectorAll('[role=tablist]').forEach(list => {
    const tabs = [...list.querySelectorAll('[role=tab]')];
    const select = tab => tabs.forEach(t => {
      const on = t === tab;
      t.setAttribute('aria-selected', on);
      t.tabIndex = on ? 0 : -1;
      document.getElementById(t.getAttribute('aria-controls')).hidden = !on;
    });
    list.addEventListener('click', e => { const t = e.target.closest('[role=tab]'); if (t) select(t); });
    list.addEventListener('keydown', e => {
      const step = { ArrowRight: 1, ArrowLeft: -1 }[e.key];
      if (!step) return;
      const next = tabs[(tabs.indexOf(document.activeElement) + step + tabs.length) % tabs.length];
      select(next); next.focus();
    });
  });
</script>
```

### Timeline / pasos de un plan

```html
<ol class="relative space-y-6 border-l border-[var(--va-hairline)] pl-6">
  <li class="relative">
    <span class="absolute -left-[31px] top-1 size-3 rounded-full bg-[var(--va-ok)] ring-4 ring-[var(--card)]"></span>
    <p class="font-semibold">Extraer el cliente HTTP</p>
    <p class="va-body text-sm">3 archivos · sin cambios de comportamiento</p>
  </li>
  <li class="relative">
    <span class="absolute -left-[31px] top-1 size-3 rounded-full border-2 border-[var(--muted-foreground)] bg-[var(--card)] ring-4 ring-[var(--card)]"></span>
    <p class="font-semibold">Añadir reintentos con backoff</p>
  </li>
</ol>
```

### Tabla de detalle

```html
<div class="overflow-x-auto">
  <table class="w-full text-sm">
    <thead class="va-label text-left">
      <tr class="border-b border-[var(--va-hairline)]"><th class="py-2 pr-4">Endpoint</th><th class="py-2 text-right">p95</th></tr>
    </thead>
    <tbody class="[&>tr:hover]:bg-[var(--va-sunken)]">
      <tr class="border-b border-[var(--va-hairline)]"><td class="py-2 pr-4 font-mono text-[13px]">/search</td><td class="py-2 text-right">212 ms</td></tr>
    </tbody>
  </table>
</div>
```

Los números van alineados a la derecha y el texto a la izquierda. La tabla nunca es el elemento
dominante: es el detalle que respalda la gráfica.

## Iconos

Usa SVG inline con trazo de 1.5–2, `stroke="currentColor"`, `fill="none"` y un tamaño de 16–20px.
Pocos iconos y con significado: un icono por sección como máximo.
