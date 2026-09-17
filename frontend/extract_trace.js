const fs = require('fs');
const JSZip = require('jszip');

async function extract() {
    const data = fs.readFileSync('frontend/test-results/portfolio-Critical-Flows-P-6419d-l-PAPER-portfolio-lifecycle-desktop-1920x1080/trace.zip');
    const zip = await JSZip.loadAsync(data);
    
    // Read network.json or .trace file
    const file = Object.keys(zip.files).find(f => f.endsWith('.trace'));
    if (!file) {
        console.log("No .trace file found");
        return;
    }
    
    // .trace files contain JSONL
    const content = await zip.file(file).async("string");
    const lines = content.split('\n');
    for (const line of lines) {
        if (!line.trim()) continue;
        try {
            const obj = JSON.parse(line);
            if (obj.type === 'console') {
                console.log('CONSOLE:', obj.text);
            }
            if (obj.type === 'pageError') {
                console.log('PAGE ERROR:', obj.error);
            }
            if (obj.type === 'request' && obj.url && obj.url.includes('/api/v1')) {
                console.log('REQ:', obj.method, obj.url);
            }
        } catch(e) {}
    }
}
extract();
