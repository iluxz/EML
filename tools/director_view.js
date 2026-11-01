'use strict';
const fs = require('fs');
const { parse } = require('D:/Multipurpose/other projects/EML Files/src/edith');

function parseDirector(file) {
    const src = fs.readFileSync(file, 'utf16le');
    const ast = parse(src);
    const dir = ast.root.block.find(n => n.words[0].v === 'director');
    if (!dir || !dir.block) return null;

    const getVal = (node, key) => {
        const s = node.block.find(n => !n.block && n.words[0] && n.words[0].v === key);
        return s ? s.words.slice(1).map(w => w.v).join(' ') : null;
    };

    const x = parseInt(getVal(dir, 'x') || '0');
    const y = parseInt(getVal(dir, 'y') || '0');

    const nodesBlock = dir.block.find(n => n.words[0].v === 'nodes');
    const linksBlock = dir.block.find(n => n.words[0].v === 'links');

    const nodes = [];
    if (nodesBlock && nodesBlock.block) {
        for (const n of nodesBlock.block) {
            const node = {
                type: n.words[0].v,
                name: n.words[1] ? n.words[1].v : n.words[0].v,
                x: parseInt(getVal(n, 'x') || '0'),
                y: parseInt(getVal(n, 'y') || '0'),
                index: parseInt(getVal(n, 'index') || '-1'),
                props: {},
                inputs: new Set(),
                outputs: new Set(),
            };
            if (n.block) {
                for (const c of n.block) {
                    if (!c.block) {
                        node.props[c.words[0].v] = c.words.slice(1).map(w => w.v).join(' ');
                    }
                }
            }
            nodes.push(node);
        }
    }

    const links = [];
    if (linksBlock && linksBlock.block) {
        for (const l of linksBlock.block) {
            const link = { inputIdx: -1, inputPin: '', outputIdx: -1, outputPin: '' };
            if (l.block) {
                const inp = l.block.find(n => !n.block && n.words[0] && n.words[0].v === 'input');
                const out = l.block.find(n => !n.block && n.words[0] && n.words[0].v === 'output');
                if (inp) {
                    const parts = inp.words.slice(1).map(w => w.v);
                    link.inputIdx = parseInt(parts[0]);
                    link.inputPin = parts.slice(1).join(' ') || 'Input';
                }
                if (out) {
                    const parts = out.words.slice(1).map(w => w.v);
                    link.outputIdx = parseInt(parts[0]);
                    link.outputPin = parts.slice(1).join(' ') || 'Output';
                }
            }
            // Add pins to nodes
            const inNode = nodes.find(n => n.index === link.inputIdx);
            const outNode = nodes.find(n => n.index === link.outputIdx);
            if (inNode) inNode.inputs.add(link.inputPin);
            if (outNode) outNode.outputs.add(link.outputPin);
            links.push(link);
        }
    }

    // Add default pins for common node types
    const defaultPins = {
        Entry: { outputs: ['OnEnter'] },
        Once: { inputs: ['Input'], outputs: ['Output'] },
        ReadBool: { inputs: ['Input'], outputs: ['True', 'False'] },
        ReadInt: { inputs: ['Input'], outputs: ['Equal', 'Less', 'Greater'] },
        Button: { inputs: [], outputs: ['OnInteract'] },
        Respawn: { inputs: ['Respawn'], outputs: [] },
        WriteBool: { inputs: ['Input', 'Value'], outputs: ['Output'] },
        WriteInt: { inputs: ['Input', 'Value'], outputs: ['Output'] },
        Play: { inputs: ['Input'], outputs: ['Repeat', 'Done'] },
        Enable: { inputs: ['Enable'], outputs: [] },
        Disable: { inputs: ['Disable'], outputs: [] },
        Toggle: { inputs: ['Toggle'], outputs: [] },
    };

    for (const node of nodes) {
        const defs = defaultPins[node.type];
        if (defs) {
            for (const p of (defs.inputs || [])) node.inputs.add(p);
            for (const p of (defs.outputs || [])) node.outputs.add(p);
        }
        node.inputs = Array.from(node.inputs);
        node.outputs = Array.from(node.outputs);
    }

    return { x, y, nodes, links };
}

const file = process.argv[2];
if (!file) {
    console.error('Usage: node director_view.js <file.edith> [output.html]');
    process.exit(1);
}

const result = parseDirector(file);
if (!result) {
    console.error('No director block found');
    process.exit(1);
}

const outPath = process.argv[3] || file.replace('.edith', '_director.html');

// Build HTML
var html = '';
html += '<!DOCTYPE html>\n';
html += '<html>\n<head>\n<meta charset="utf-8">\n';
html += '<title>Director Graph</title>\n';
html += '<style>\n';
html += 'body { margin: 0; background: #2b2b2b; color: #ddd; font-family: "Segoe UI", Arial, sans-serif; overflow: hidden; }\n';
html += '#canvas { width: 100vw; height: 100vh; cursor: grab; }\n';
html += '.node rect.header { fill: #1a1a1a; }\n';
html += '.node rect.body { fill: #3a3a3a; stroke: #555; stroke-width: 1; }\n';
html += '.node text.header { fill: #fff; font-size: 12px; font-weight: bold; text-anchor: middle; }\n';
html += '.node text.pin { fill: #ccc; font-size: 10px; }\n';
html += '.pin-circle { fill: #bbb; stroke: #222; stroke-width: 1; }\n';
html += '.pin-circle:hover { fill: #6af; }\n';
html += '.link { stroke: #bbb; stroke-width: 2; fill: none; }\n';
html += '.link:hover { stroke: #6af; }\n';
html += '.title { position: fixed; top: 10px; left: 10px; background: rgba(40,40,40,0.95); padding: 10px; border-radius: 6px; z-index: 10; color: #eee; border: 1px solid #555; font-size: 13px; }\n';
html += '#panel { position: fixed; right: 10px; top: 10px; width: 280px; background: rgba(40,40,40,0.95); padding: 12px; border-radius: 6px; z-index: 10; color: #eee; border: 1px solid #555; display: none; font-size: 12px; }\n';
html += '#panel h3 { margin: 0 0 10px 0; font-size: 14px; color: #6af; }\n';
html += '#panel .prop { margin: 3px 0; }\n';
html += '#panel .prop-key { color: #999; }\n';
html += '</style>\n</head>\n<body>\n';
html += '<div class="title">Director Graph: ' + file.split(/[\\/]/).pop() + ' | Nodes: ' + result.nodes.length + ' | Links: ' + result.links.length + '<br>Drag to pan &bull; Scroll to zoom &bull; Click node for details</div>\n';
html += '<button id="autolayout" style="position:fixed;top:70px;left:10px;z-index:11;padding:6px 12px;background:#4a90d9;color:#fff;border:none;border-radius:4px;cursor:pointer;font-family:Arial;font-size:12px;">Auto Layout</button>\n';
html += '<div id="panel"></div>\n';
html += '<svg id="canvas" xmlns="http://www.w3.org/2000/svg"></svg>\n';
html += '<script>\n';
html += 'const data = ' + JSON.stringify(result) + ';\n';
html += 'const svg = document.getElementById("canvas");\n';
html += 'const panel = document.getElementById("panel");\n';
html += 'let panX = 0;\n';
html += 'let panY = 0;\n';
html += 'let scale = 1.0;\n';
html += 'let isDragging = false;\n';
html += 'let dragStartX = 0, dragStartY = 0, panStartX = 0, panStartY = 0;\n';

html += 'let dragMoved = false;\n';
html += 'svg.addEventListener("mousedown", function(e) { if (e.button === 0) { isDragging = true; dragMoved = false; dragStartX = e.clientX; dragStartY = e.clientY; panStartX = panX; panStartY = panY; svg.style.cursor = "grabbing"; } });\n';
html += 'svg.addEventListener("mousemove", function(e) { if (isDragging) { dragMoved = true; panX = panStartX + (e.clientX - dragStartX); panY = panStartY + (e.clientY - dragStartY); redraw(); } });\n';
html += 'svg.addEventListener("mouseup", function(e) { isDragging = false; svg.style.cursor = "grab"; });\n';
html += 'svg.addEventListener("mouseleave", function(e) { isDragging = false; svg.style.cursor = "grab"; });\n';
html += 'svg.addEventListener("wheel", function(e) { e.preventDefault(); const zf = e.deltaY < 0 ? 1.1 : 0.9; scale *= zf; scale = Math.max(0.2, Math.min(5, scale)); redraw(); });\n';
html += 'svg.style.cursor = "grab";\n';

html += 'function toScreen(nx, ny) {\n';
html += '    return {\n';
html += '        x: (nx + panX) * scale + (1 - scale) * window.innerWidth / 2,\n';
html += '        y: (ny + panY) * scale + (1 - scale) * window.innerHeight / 2\n';
html += '    };\n';
html += '}\n';

html += 'function redraw() {\n';
html += '    svg.innerHTML = "";\n';
html += '    const pinPos = {};\n';
html += '    const nodePos = {};\n';
html += '    const nodeHeight = {};\n';
html += '    const nodeWidth = 180;\n';
html += '    const headerH = 24;\n';
html += '    const rowH = 20;\n';
html += '    const pinR = 5;\n';

// Compute node geometry and positions
html += '    for (const node of data.nodes) {\n';
html += '        const rows = Math.max(node.inputs.length, node.outputs.length, 1);\n';
html += '        nodeHeight[node.index] = headerH + rows * rowH + 8;\n';
html += '        nodePos[node.index] = toScreen(node.x, node.y);\n';
html += '        pinPos[node.index] = {};\n';
html += '        const pos = nodePos[node.index];\n';
html += '        const w = nodeWidth * scale;\n';
html += '        const hh = headerH * scale;\n';
html += '        const rh = rowH * scale;\n';
html += '        for (let i = 0; i < node.inputs.length; i++) {\n';
html += '            pinPos[node.index][node.inputs[i]] = { x: pos.x - w/2, y: pos.y + hh + (i + 0.6) * rh };\n';
html += '        }\n';
html += '        for (let i = 0; i < node.outputs.length; i++) {\n';
html += '            pinPos[node.index][node.outputs[i]] = { x: pos.x + w/2, y: pos.y + hh + (i + 0.6) * rh };\n';
html += '        }\n';
html += '    }\n';

// Draw links first (behind nodes)
html += '    for (const link of data.links) {\n';
html += '        if (!pinPos[link.outputIdx] || !pinPos[link.inputIdx]) continue;\n';
html += '        const p1 = pinPos[link.outputIdx][link.outputPin];\n';
html += '        const p2 = pinPos[link.inputIdx][link.inputPin];\n';
html += '        if (!p1 || !p2) continue;\n';
html += '        const dx = Math.abs(p2.x - p1.x) * 0.5;\n';
html += '        const d = "M " + p1.x + " " + p1.y + " C " + (p1.x + dx) + " " + p1.y + ", " + (p2.x - dx) + " " + p2.y + ", " + p2.x + " " + p2.y;\n';
html += '        const path = document.createElementNS("http://www.w3.org/2000/svg", "path");\n';
html += '        path.setAttribute("d", d);\n';
html += '        path.setAttribute("class", "link");\n';
html += '        svg.appendChild(path);\n';
html += '    }\n';

// Draw nodes
html += '    for (const node of data.nodes) {\n';
html += '        const pos = nodePos[node.index];\n';
html += '        const h = nodeHeight[node.index];\n';
html += '        const w = nodeWidth * scale;\n';
html += '        const hh = headerH * scale;\n';
html += '        const rh = rowH * scale;\n';
html += '        const r = pinR * scale;\n';
html += '        const g = document.createElementNS("http://www.w3.org/2000/svg", "g");\n';
html += '        g.setAttribute("class", "node");\n';
html += '        g.style.cursor = "pointer";\n';

// Body rect
html += '        const body = document.createElementNS("http://www.w3.org/2000/svg", "rect");\n';
html += '        body.setAttribute("x", pos.x - w/2);\n';
html += '        body.setAttribute("y", pos.y);\n';
html += '        body.setAttribute("width", w);\n';
html += '        body.setAttribute("height", h * scale);\n';
html += '        body.setAttribute("rx", 6 * scale);\n';
html += '        body.setAttribute("class", "body");\n';
html += '        g.appendChild(body);\n';

// Header rect
html += '        const head = document.createElementNS("http://www.w3.org/2000/svg", "rect");\n';
html += '        head.setAttribute("x", pos.x - w/2);\n';
html += '        head.setAttribute("y", pos.y);\n';
html += '        head.setAttribute("width", w);\n';
html += '        head.setAttribute("height", hh);\n';
html += '        head.setAttribute("rx", 6 * scale);\n';
html += '        head.setAttribute("class", "header");\n';
html += '        g.appendChild(head);\n';

// Header text
html += '        const title = document.createElementNS("http://www.w3.org/2000/svg", "text");\n';
html += '        title.setAttribute("x", pos.x);\n';
html += '        title.setAttribute("y", pos.y + hh * 0.65);\n';
html += '        title.setAttribute("class", "header");\n';
html += '        title.setAttribute("font-size", (12 * scale) + "px");\n';
html += '        title.textContent = node.type;\n';
html += '        g.appendChild(title);\n';

// Input pins
html += '        for (let i = 0; i < node.inputs.length; i++) {\n';
html += '            const py = pos.y + hh + (i + 0.6) * rh;\n';
html += '            const pin = document.createElementNS("http://www.w3.org/2000/svg", "circle");\n';
html += '            pin.setAttribute("cx", pos.x - w/2);\n';
html += '            pin.setAttribute("cy", py);\n';
html += '            pin.setAttribute("r", r);\n';
html += '            pin.setAttribute("class", "pin-circle");\n';
html += '            g.appendChild(pin);\n';
html += '            const lbl = document.createElementNS("http://www.w3.org/2000/svg", "text");\n';
html += '            lbl.setAttribute("x", pos.x - w/2 + r * 2 + 3);\n';
html += '            lbl.setAttribute("y", py + 3 * scale);\n';
html += '            lbl.setAttribute("class", "pin");\n';
html += '            lbl.setAttribute("font-size", (10 * scale) + "px");\n';
html += '            lbl.textContent = node.inputs[i];\n';
html += '            g.appendChild(lbl);\n';
html += '        }\n';

// Output pins
html += '        for (let i = 0; i < node.outputs.length; i++) {\n';
html += '            const py = pos.y + hh + (i + 0.6) * rh;\n';
html += '            const pin = document.createElementNS("http://www.w3.org/2000/svg", "circle");\n';
html += '            pin.setAttribute("cx", pos.x + w/2);\n';
html += '            pin.setAttribute("cy", py);\n';
html += '            pin.setAttribute("r", r);\n';
html += '            pin.setAttribute("class", "pin-circle");\n';
html += '            g.appendChild(pin);\n';
html += '            const lbl = document.createElementNS("http://www.w3.org/2000/svg", "text");\n';
html += '            lbl.setAttribute("x", pos.x + w/2 - r * 2 - 3);\n';
html += '            lbl.setAttribute("y", py + 3 * scale);\n';
html += '            lbl.setAttribute("class", "pin");\n';
html += '            lbl.setAttribute("font-size", (10 * scale) + "px");\n';
html += '            lbl.setAttribute("text-anchor", "end");\n';
html += '            lbl.textContent = node.outputs[i];\n';
html += '            g.appendChild(lbl);\n';
html += '        }\n';

// Click for details
html += '        g.addEventListener("click", function(e) {\n';
html += '            if (dragMoved) return;\n';
html += '            e.stopPropagation();\n';
html += '            let html = "<h3>" + node.type + " #" + node.index + "</h3>";\n';
html += '            for (const [k, v] of Object.entries(node.props)) {\n';
html += '                if (k === "x" || k === "y" || k === "index") continue;\n';
html += '                html += "<div class=\\"prop\\"><span class=\\"prop-key\\">" + k + ":</span> " + v + "</div>";\n';
html += '            }\n';
html += '            panel.innerHTML = html;\n';
html += '            panel.style.display = "block";\n';
html += '        });\n';
html += '        svg.appendChild(g);\n';
html += '    }\n';
html += '}\n';
html += 'function fitToScreen() {\n';
html += '    if (data.nodes.length === 0) { redraw(); return; }\n';
html += '    const nodeWidth = 180;\n';
html += '    const headerH = 24;\n';
html += '    const rowH = 20;\n';
html += '    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;\n';
html += '    for (const node of data.nodes) {\n';
html += '        const rows = Math.max(node.inputs.length, node.outputs.length, 1);\n';
html += '        const h = headerH + rows * rowH + 8;\n';
html += '        minX = Math.min(minX, node.x - nodeWidth/2);\n';
html += '        maxX = Math.max(maxX, node.x + nodeWidth/2);\n';
html += '        minY = Math.min(minY, node.y);\n';
html += '        maxY = Math.max(maxY, node.y + h);\n';
html += '    }\n';
html += '    const graphW = maxX - minX;\n';
html += '    const graphH = maxY - minY;\n';
html += '    const pad = 60;\n';
html += '    scale = Math.min((window.innerWidth - pad*2) / graphW, (window.innerHeight - pad*2) / graphH, 2);\n';
html += '    scale = Math.max(0.1, scale);\n';
html += '    panX = window.innerWidth / 2 - (minX + maxX) / 2;\n';
html += '    panY = window.innerHeight / 2 - (minY + maxY) / 2;\n';
html += '    redraw();\n';
html += '}\n';
html += 'function autoLayout() {\n';
html += '    const layerMap = {\n';
html += '        Entry: 0, Trigger: 0, Button: 0,\n';
html += '        ReadBool: 1, ReadInt: 1, Once: 1,\n';
html += '        WriteBool: 2, WriteInt: 2, Enable: 2, Disable: 2, Toggle: 2, Play: 2, Respawn: 2, Custom: 2,\n';
html += '        Achieve: 3\n';
html += '    };\n';
html += '    for (const node of data.nodes) {\n';
html += '        node._layer = layerMap[node.type] !== undefined ? layerMap[node.type] : 1;\n';
html += '    }\n';
// Propagate layers based on connections: a node should be at least one layer after its outputs
html += '    for (let pass = 0; pass < 5; pass++) {\n';
html += '        for (const link of data.links) {\n';
html += '            const src = data.nodes.find(n => n.index === link.outputIdx);\n';
html += '            const dst = data.nodes.find(n => n.index === link.inputIdx);\n';
html += '            if (src && dst && dst._layer <= src._layer) {\n';
html += '                dst._layer = src._layer + 1;\n';
html += '            }\n';
html += '        }\n';
html += '    }\n';
// Group by layer and sort by original y
html += '    const layers = {};\n';
html += '    for (const node of data.nodes) {\n';
html += '        if (!layers[node._layer]) layers[node._layer] = [];\n';
html += '        layers[node._layer].push(node);\n';
html += '    }\n';
html += '    for (const layer of Object.values(layers)) {\n';
html += '        layer.sort((a, b) => a.y - b.y);\n';
html += '    }\n';
// Position
html += '    const colW = 260;\n';
html += '    const rowH = 70;\n';
html += '    const layerKeys = Object.keys(layers).map(Number).sort((a,b)=>a-b);\n';
html += '    for (const layerIdx of layerKeys) {\n';
html += '        const layer = layers[layerIdx];\n';
html += '        for (let i = 0; i < layer.length; i++) {\n';
html += '            layer[i].x = layerIdx * colW;\n';
html += '            layer[i].y = i * rowH;\n';
html += '        }\n';
html += '    }\n';
html += '    fitToScreen();\n';
html += '}\n';
html += 'document.getElementById("autolayout").addEventListener("click", autoLayout);\n';
html += 'fitToScreen();\n';
html += 'svg.addEventListener("click", function(e) { if (e.target === svg) panel.style.display = "none"; });\n';
html += '</script>\n</body>\n</html>\n';

fs.writeFileSync(outPath, html);
console.log('Wrote viewer: ' + outPath);
console.log('Nodes: ' + result.nodes.length + ', Links: ' + result.links.length);
