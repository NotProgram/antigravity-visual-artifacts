# Gráficas y diagramas con SVG inline

El CSP bloquea Chart.js, D3 y Mermaid, así que todo se dibuja con SVG. Las funciones de abajo miden
el ancho real del contenedor y dibujan con `viewBox` en píxeles reales, lo que mantiene el texto a
12px o más en cualquier pantalla. Copia el bloque **helpers** una vez y luego solo las gráficas que
uses. Requiere el bloque base de [design-system.md](./design-system.md) (`--va-s1..5`).

## Elegir la gráfica

| Pregunta | Gráfica |
|---|---|
| ¿Cuál es mayor? (categorías) | Barras horizontales, ordenadas, con la clave resaltada |
| ¿Cómo evolucionó? (tiempo) | Línea con etiqueta al final de cada serie |
| ¿Qué parte del total? (≤5 partes) | Donut con el total en el centro. Con más de 5 partes, usa barras |
| Tendencia dentro de un KPI | Sparkline |

Reglas: máximo 5 series. Una sola serie resaltada en `--va-s1` y el resto apagadas cuando hay una
conclusión. Etiquetas directas mejor que leyenda. Ejes con unidad. La rejilla, tenue o ausente.

## Helpers (obligatorio si usas gráficas)

```html
<style>
  .va-chart { display: block; width: 100%; overflow: visible; }
  .va-axis  { font-size: 12px; fill: var(--muted-foreground); }
  .va-value { font-size: 12px; font-weight: 600; fill: var(--foreground); }
  .va-grid  { stroke: var(--va-hairline); stroke-width: 1; }
  .va-guide { stroke: var(--muted-foreground); stroke-dasharray: 3 3; }
  .va-tip { position: absolute; z-index: 2; pointer-events: none; display: grid; gap: 4px; min-width: 140px;
    padding: 8px 10px; border-radius: var(--va-radius-sm); font-size: 12px; white-space: nowrap;
    background: var(--card); border: 1px solid var(--border); box-shadow: var(--va-shadow); }
  .va-tip[hidden] { display: none; }
  .va-tip-row { display: flex; align-items: center; gap: 6px; color: var(--muted-foreground); }
  .va-tip-row i { width: 8px; height: 8px; border-radius: 2px; flex: none; }
</style>
<script>
  const VA_NS = 'http://www.w3.org/2000/svg';
  const vaEl = (tag, attrs = {}, text) => {
    const el = document.createElementNS(VA_NS, tag);
    Object.entries(attrs).forEach(([k, v]) => el.setAttribute(k, v));
    if (text != null) el.textContent = text;
    return el;
  };
  const vaNiceMax = v => {
    const p = 10 ** Math.floor(Math.log10(v || 1));
    const step = [1, 2, 2.5, 5, 10].find(s => s * p >= v);
    return step * p;
  };
  const vaFmt = n => n.toLocaleString('es', { maximumFractionDigits: 1 });
  // Dibuja con el ancho real del contenedor y redibuja al cambiar de tamaño.
  const vaMount = (svg, draw) => {
    const render = () => {
      const w = Math.round(svg.parentElement.clientWidth);
      if (!w) return;
      svg.replaceChildren();
      const h = draw(svg, w);
      svg.setAttribute('viewBox', `0 0 ${w} ${h}`);
      svg.setAttribute('height', h);
    };
    new ResizeObserver(render).observe(svg.parentElement);
  };
  // Tooltip con línea guía: una banda invisible por cada punto del eje X.
  // rowsAt(i) devuelve [titulo, [color, texto], ...]. El SVG debe ir solo dentro de un <div>.
  const vaHover = (s, { n, x, top, bottom, W }, rowsAt) => {
    const box = s.parentElement;
    box.style.position = 'relative';
    const tip = box.querySelector('.va-tip')
      || box.appendChild(Object.assign(document.createElement('div'), { className: 'va-tip', hidden: true }));
    const guide = vaEl('line', { y1: top, y2: bottom, class: 'va-guide', visibility: 'hidden' });
    s.append(guide);
    const band = n > 1 ? x(1) - x(0) : W;
    for (let i = 0; i < n; i++) {
      const hit = vaEl('rect', { x: x(i) - band / 2, y: top, width: band, height: bottom - top, fill: 'transparent' });
      hit.addEventListener('pointerenter', () => {
        const [title, ...rows] = rowsAt(i);
        tip.replaceChildren(Object.assign(document.createElement('strong'), { textContent: title }),
          ...rows.map(([color, text]) => {
            const row = Object.assign(document.createElement('span'), { className: 'va-tip-row', textContent: text });
            const dot = document.createElement('i');
            dot.style.background = color;
            row.prepend(dot);
            return row;
          }));
        const flip = x(i) > W / 2;
        tip.style.left = `${x(i) + (flip ? -12 : 12)}px`;
        tip.style.top = `${top}px`;
        tip.style.transform = flip ? 'translateX(-100%)' : 'none';
        tip.hidden = false;
        guide.setAttribute('x1', x(i));
        guide.setAttribute('x2', x(i));
        guide.setAttribute('visibility', 'visible');
      });
      hit.addEventListener('pointerleave', () => { tip.hidden = true; guide.setAttribute('visibility', 'hidden'); });
      s.append(hit);
    }
  };
</script>
```

Cada gráfica va en `<figure>` con un `<figcaption>` que dice la conclusión, y el SVG lleva
`role="img"` y `aria-label`.

## Barras horizontales

```html
<figure>
  <svg id="bars" class="va-chart" role="img" aria-label="p95 por endpoint"></svg>
  <figcaption class="va-body text-sm mt-2">/search sigue siendo el más lento.</figcaption>
</figure>
<script>
  const vaBars = (svg, rows, { unit = '', highlight } = {}) => vaMount(svg, (s, W) => {
    const rowH = 34, labelW = Math.min(160, W * 0.32), valueW = 72;
    const max = Math.max(...rows.map(r => r.value));
    rows.forEach((r, i) => {
      const y = i * rowH, w = Math.max(2, (W - labelW - valueW) * r.value / max);
      const on = highlight == null || r.label === highlight;
      s.append(
        vaEl('text', { x: labelW - 12, y: y + rowH / 2, 'text-anchor': 'end', 'dominant-baseline': 'middle', class: 'va-axis' }, r.label),
        vaEl('rect', { x: labelW, y: y + 8, width: w, height: rowH - 16, rx: 4,
          style: `fill: ${on ? 'var(--va-s1)' : 'color-mix(in srgb, var(--muted-foreground) 30%, transparent)'}` }),
        vaEl('text', { x: labelW + w + 8, y: y + rowH / 2, 'dominant-baseline': 'middle', class: 'va-value' }, vaFmt(r.value) + unit)
      );
    });
    return rows.length * rowH;
  });
  vaBars(document.getElementById('bars'),
    [{ label: '/search', value: 212 }, { label: '/hotels', value: 140 }, { label: '/auth', value: 48 }],
    { unit: ' ms', highlight: '/search' });
</script>
```

## Línea (series temporales)

```js
// series: [{ name, values: [n...], muted? }], labels: ['L','M',...] (mismo largo que values)
// muted: true apaga una serie de contexto (p. ej. la semana anterior) para que destaque la clave.
const vaLine = (svg, series, { labels = [], unit = '', height = 240 } = {}) => vaMount(svg, (s, W) => {
  const pad = { t: 12, r: 84, b: 28, l: 44 }, H = height;
  const n = labels.length || series[0].values.length;
  const max = vaNiceMax(Math.max(...series.flatMap(x => x.values)));
  const x = i => pad.l + i * (W - pad.l - pad.r) / Math.max(1, n - 1);
  const y = v => pad.t + (H - pad.t - pad.b) * (1 - v / max);
  for (let k = 0; k <= 4; k++) {
    const v = max * k / 4;
    s.append(vaEl('line', { x1: pad.l, x2: W - pad.r, y1: y(v), y2: y(v), class: 'va-grid' }),
             vaEl('text', { x: pad.l - 8, y: y(v), 'text-anchor': 'end', 'dominant-baseline': 'middle', class: 'va-axis' }, vaFmt(v)));
  }
  const every = Math.ceil(n / Math.max(2, Math.floor((W - pad.l - pad.r) / 64)));
  labels.forEach((l, i) => (i % every === 0 || i === n - 1) &&
    s.append(vaEl('text', { x: x(i), y: H - 8, 'text-anchor': 'middle', class: 'va-axis' }, l)));
  series.forEach((ser, si) => {
    const color = ser.muted ? 'var(--muted-foreground)' : `var(--va-s${si + 1})`, last = ser.values.length - 1;
    const d = ser.values.map((v, i) => `${i ? 'L' : 'M'}${x(i)},${y(v)}`).join('');
    s.append(
      vaEl('path', { d, fill: 'none', 'stroke-width': 2.25, 'stroke-linejoin': 'round', 'stroke-linecap': 'round', style: `stroke: ${color}` }),
      vaEl('circle', { cx: x(last), cy: y(ser.values[last]), r: 3.5, style: `fill: ${color}` }),
      vaEl('text', { x: x(last) + 8, y: y(ser.values[last]) - 8, 'dominant-baseline': 'middle', class: 'va-value', style: `fill: ${color}` },
        vaFmt(ser.values[last]) + unit),
      vaEl('text', { x: x(last) + 8, y: y(ser.values[last]) + 8, 'dominant-baseline': 'middle', class: 'va-axis' }, ser.name)
    );
  });
  vaHover(s, { n, x, top: pad.t, bottom: H - pad.b, W }, i => [
    labels[i] ?? '',
    ...series.map((ser, si) => [ser.muted ? 'var(--muted-foreground)' : `var(--va-s${si + 1})`,
      `${ser.name}: ${vaFmt(ser.values[i])}${unit}`]),
  ]);
  return H;
});
```

La etiqueta final ocupa dos líneas (valor y nombre) para caber en `pad.r`. Si dos series terminan a
menos de 32px entre sí, sus etiquetas se pisan: desplaza una o quita el nombre de la menos importante.

## Donut (parte de un total)

```js
// parts: [{ label, value }], máximo 5. Dibuja el anillo y una lista de etiquetas a la derecha.
const vaDonut = (svg, parts, { center = '' } = {}) => vaMount(svg, (s, W) => {
  const size = Math.min(180, W * 0.45), r = size / 2 - 14, cx = size / 2, cy = size / 2;
  const total = parts.reduce((a, p) => a + p.value, 0);
  let acc = 0;
  parts.forEach((p, i) => {
    const pct = p.value / total * 100;
    s.append(vaEl('circle', { cx, cy, r, fill: 'none', 'stroke-width': 18, pathLength: 100,
      'stroke-dasharray': `${Math.max(0, pct - 0.6)} ${100 - pct + 0.6}`, 'stroke-dashoffset': 25 - acc,
      style: `stroke: var(--va-s${i + 1})` }));
    acc += pct;
    const ly = 20 + i * 26;
    s.append(vaEl('rect', { x: size + 16, y: ly - 6, width: 10, height: 10, rx: 2, style: `fill: var(--va-s${i + 1})` }),
             vaEl('text', { x: size + 32, y: ly, 'dominant-baseline': 'middle', class: 'va-axis' }, `${p.label} · ${Math.round(pct)}%`));
  });
  s.append(vaEl('text', { x: cx, y: cy, 'text-anchor': 'middle', 'dominant-baseline': 'middle', class: 'va-value', style: 'font-size: 20px' }, center || vaFmt(total)));
  return Math.max(size, parts.length * 26 + 16);
});
```

## Sparkline (dentro de un KPI)

```js
const vaSpark = (svg, values, { height = 36 } = {}) => vaMount(svg, (s, W) => {
  const min = Math.min(...values), max = Math.max(...values), span = max - min || 1;
  const pt = (v, i) => [2 + i * (W - 6) / (values.length - 1), 3 + (height - 6) * (1 - (v - min) / span)];
  const pts = values.map(pt);
  s.append(
    vaEl('polyline', { points: pts.join(' '), fill: 'none', 'stroke-width': 1.75, style: 'stroke: var(--va-s1)' }),
    vaEl('circle', { cx: pts.at(-1)[0], cy: pts.at(-1)[1], r: 2.5, style: 'fill: var(--va-s1)' })
  );
  return height;
});
```

## Diagramas (arquitectura, flujo, secuencia)

Un buen diagrama muestra **el mecanismo real**: qué componente llama a cuál, con qué dato y en qué
orden. No dibujes cajas genéricas con "Frontend → Backend → DB" si la conversación tiene detalles
concretos.

1. Haz una lista de nodos y aristas antes de dibujar. Ninguna arista sin etiqueta si transporta algo.
2. Coloca los nodos en una rejilla: columnas = capas o etapas, filas = alternativas.
3. Resalta el camino del que trata la explicación (trazo `--primary`, 2px) y apaga el resto
   (`--muted-foreground` al 40%).
4. Si el diagrama es ancho, ponle `min-width` y un contenedor con scroll horizontal propio, así el
   texto no baja de 12px en el móvil.

```html
<div class="overflow-x-auto">
  <svg viewBox="0 0 720 200" class="w-full" style="min-width: 560px" role="img"
       aria-label="Flujo de un pedido: tienda, cola de trabajos y pasarela de pago">
    <defs>
      <marker id="va-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
        <path d="M0,0 L10,5 L0,10 z" style="fill: context-stroke"/>
      </marker>
    </defs>
    <style>
      .node rect { fill: var(--card); stroke: var(--border); }
      .node.is-focus rect { stroke: var(--primary); stroke-width: 2;
        fill: color-mix(in oklch, var(--primary) 8%, var(--card)); }
      .node .t { font-size: 14px; font-weight: 600; fill: var(--foreground); }
      .node .s { font-size: 12px; fill: var(--muted-foreground); }
      .edge { fill: none; stroke: color-mix(in srgb, var(--muted-foreground) 60%, transparent); stroke-width: 1.5; }
      .edge.is-focus { stroke: var(--primary); stroke-width: 2; }
      .edge-label { font-size: 12px; fill: var(--muted-foreground); }
    </style>
    <g class="node"><rect x="10" y="70" width="170" height="60" rx="10"/>
      <text class="t" x="95" y="96" text-anchor="middle">Tienda web</text>
      <text class="s" x="95" y="116" text-anchor="middle">crea el pedido</text></g>
    <g class="node is-focus"><rect x="275" y="70" width="170" height="60" rx="10"/>
      <text class="t" x="360" y="96" text-anchor="middle">Cola · worker</text>
      <text class="s" x="360" y="116" text-anchor="middle">valida y reintenta</text></g>
    <g class="node"><rect x="540" y="70" width="170" height="60" rx="10"/>
      <text class="t" x="625" y="96" text-anchor="middle">Pasarela de pago</text>
      <text class="s" x="625" y="116" text-anchor="middle">/charges</text></g>
    <path class="edge" d="M180,100 H271" marker-end="url(#va-arrow)"/>
    <text class="edge-label" x="227" y="90" text-anchor="middle">evento</text>
    <path class="edge is-focus" d="M445,100 H536" marker-end="url(#va-arrow)"/>
    <text class="edge-label" x="490" y="90" text-anchor="middle">POST JSON</text>
  </svg>
</div>
```

Para flechas que doblan, usa un path ortogonal (`M x1,y1 H xm V y2 H x2`) en lugar de diagonales.
Si hay más de 8 nodos, divide el diagrama en dos o usa tabs (uno por escenario).
