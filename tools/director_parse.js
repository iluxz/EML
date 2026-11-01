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
            };
            // Collect all properties
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
            const link = {
                input: null,
                output: null,
            };
            if (l.block) {
                const inp = l.block.find(n => !n.block && n.words[0] && n.words[0].v === 'input');
                const out = l.block.find(n => !n.block && n.words[0] && n.words[0].v === 'output');
                if (inp) link.input = inp.words.slice(1).map(w => w.v).join(' ');
                if (out) link.output = out.words.slice(1).map(w => w.v).join(' ');
            }
            links.push(link);
        }
    }

    return { x, y, nodes, links };
}

// CLI
const file = process.argv[2];
if (!file) {
    console.error('Usage: node director_parse.js <file.edith>');
    process.exit(1);
}
const result = parseDirector(file);
if (!result) {
    console.error('No director block found');
    process.exit(1);
}
console.log(JSON.stringify(result, null, 2));
