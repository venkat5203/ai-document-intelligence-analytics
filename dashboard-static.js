const DATA_URL = "assets/dashboard-data.json";
let dashboardData = null;
let lastVisibleRecords = [];
const $ = (id) => document.getElementById(id);
const number = (n) => Number(n || 0).toLocaleString("en-IN");
const money = (n) => n == null ? "—" : "₹" + Number(n).toLocaleString("en-IN", { maximumFractionDigits: 0 });

function selected() {
  return { category: $("categoryFilter").value, region: $("regionFilter").value, quality: $("qualityFilter").value };
}
function rowMatches(row, filters) {
  return (filters.category === "all" || row.category === filters.category) &&
    (filters.region === "all" || row.region === filters.region) &&
    (filters.quality === "all" || (filters.quality === "valid" ? row.valid : !row.valid));
}
function filteredCross(filters) { return dashboardData.cross.filter((r) => rowMatches(r, filters)); }
function aggregateMetrics(filters) {
  const rows = filteredCross(filters);
  let total = 0, valid = 0, weightedQuality = 0;
  rows.forEach((r) => { total += r.count; if (r.valid) valid += r.count; weightedQuality += r.avg_quality * r.count; });
  const exceptions = total - valid;
  return { total, valid, exceptions, pass: total ? valid / total * 100 : 0, quality: total ? weightedQuality / total : 0 };
}
function updateKpis(filters) {
  const m = aggregateMetrics(filters);
  $("kpiTotal").textContent = number(m.total);
  $("kpiPass").textContent = m.total ? m.pass.toFixed(1) + "%" : "—";
  $("kpiExceptions").textContent = number(m.exceptions);
  $("kpiQuality").textContent = m.total ? m.quality.toFixed(1) + "%" : "—";
}
function monthlyValues(filters) {
  const rows = dashboardData.monthly.filter((r) => rowMatches(r, filters));
  const map = new Map(); rows.forEach((r) => map.set(r.month, (map.get(r.month) || 0) + r.count));
  return [...map.entries()].sort((a,b) => a[0].localeCompare(b[0]));
}
function categoryValues(filters) {
  const rows = filteredCross(filters); const map = new Map();
  rows.forEach((r) => map.set(r.category, (map.get(r.category) || 0) + r.count));
  return [...map.entries()].sort((a,b) => b[1] - a[1]);
}
function issueValues(filters) {
  if (filters.quality === "valid") return [];
  const rows = dashboardData.issues.filter((r) => (filters.category === "all" || r.category === filters.category) && (filters.region === "all" || r.region === filters.region));
  const map = new Map(); rows.forEach((r) => map.set(r.issue, (map.get(r.issue) || 0) + r.count));
  return [...map.entries()].sort((a,b) => b[1] - a[1]);
}
function setupCanvas(canvas) {
  const rect = canvas.getBoundingClientRect(); const ratio = window.devicePixelRatio || 1;
  canvas.width = Math.max(1, rect.width * ratio); canvas.height = Math.max(1, Number(canvas.getAttribute("height") || 220) * ratio);
  const ctx = canvas.getContext("2d"); ctx.setTransform(ratio,0,0,ratio,0,0); return { ctx, width: rect.width, height: Number(canvas.getAttribute("height") || 220) };
}
function drawLineChart(canvas, rows) {
  const {ctx,w,h}=(()=>{const o=setupCanvas(canvas);return {ctx:o.ctx,w:o.width,h:o.height};})();
  ctx.clearRect(0,0,w,h); const left=42,right=12,top=12,bottom=34, cw=w-left-right,ch=h-top-bottom;
  if (!rows.length) { ctx.fillStyle="#8da2b7";ctx.fillText("No records for this filter",left,top+35);return; }
  const max=Math.max(...rows.map(r=>r[1]),1); ctx.font="10px DM Mono, monospace"; ctx.strokeStyle="#263a50";ctx.fillStyle="#8198ae";ctx.lineWidth=1;
  for(let i=0;i<4;i++){const y=top+ch*i/3;ctx.beginPath();ctx.moveTo(left,y);ctx.lineTo(w-right,y);ctx.stroke();ctx.fillText(number(Math.round(max*(1-i/3))),3,y+3);}
  const points=rows.map((r,i)=>({x:left+(rows.length===1?cw/2:cw*i/(rows.length-1)),y:top+ch-(r[1]/max)*ch}));
  const grad=ctx.createLinearGradient(0,top,0,top+ch);grad.addColorStop(0,"rgba(99,230,190,.22)");grad.addColorStop(1,"rgba(99,230,190,0)");
  ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));ctx.lineTo(points[points.length-1].x,top+ch);ctx.lineTo(points[0].x,top+ch);ctx.closePath();ctx.fillStyle=grad;ctx.fill();
  ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));ctx.strokeStyle="#63e6be";ctx.lineWidth=2.5;ctx.stroke();
  points.forEach((p,i)=>{ctx.beginPath();ctx.arc(p.x,p.y,3,0,Math.PI*2);ctx.fillStyle="#63e6be";ctx.fill();if(i%Math.max(1,Math.ceil(rows.length/6))===0||i===rows.length-1){ctx.fillStyle="#8ea4b9";ctx.textAlign="center";ctx.fillText(rows[i][0].slice(2),p.x,h-10);}});ctx.textAlign="left";
}
function drawBarChart(canvas, rows) {
  const {ctx,w,h}=(()=>{const o=setupCanvas(canvas);return {ctx:o.ctx,w:o.width,h:o.height};})();ctx.clearRect(0,0,w,h);
  if(!rows.length){ctx.fillStyle="#8da2b7";ctx.fillText("No records for this filter",14,35);return;}
  const max=Math.max(...rows.map(r=>r[1]),1),labelW=Math.min(118,w*.38),top=10,rowH=Math.min(37,(h-20)/rows.length),barMax=w-labelW-58;
  ctx.font="10px Manrope, sans-serif";
  rows.forEach((r,i)=>{const y=top+i*rowH;ctx.fillStyle="#a9bbce";ctx.textAlign="left";ctx.fillText(r[0].length>18?r[0].slice(0,17)+"…":r[0],0,y+13);ctx.fillStyle="#233a50";ctx.fillRect(labelW,y+2,barMax,12);ctx.fillStyle="#63e6be";ctx.fillRect(labelW,y+2,Math.max(2,barMax*r[1]/max),12);ctx.fillStyle="#9ab0c4";ctx.textAlign="right";ctx.fillText(number(r[1]),w-2,y+13);});
}
function drawDonut(canvas, metrics) {
  const {ctx,w,h}=(()=>{const o=setupCanvas(canvas);return {ctx:o.ctx,w:o.width,h:o.height};})();ctx.clearRect(0,0,w,h);const cx=w/2,cy=h/2,r=Math.min(w*.28,h*.38),inner=r*.67;
  const total=metrics.valid+metrics.exceptions;if(!total){ctx.fillStyle="#8da2b7";ctx.fillText("No records",cx-25,cy);return;}
  const angle=2*Math.PI*metrics.valid/total;ctx.lineWidth=r-inner;ctx.beginPath();ctx.arc(cx,cy,r-(r-inner)/2,-Math.PI/2,Math.PI*1.5);ctx.strokeStyle="#354b61";ctx.stroke();ctx.beginPath();ctx.arc(cx,cy,r-(r-inner)/2,-Math.PI/2,-Math.PI/2+angle);ctx.strokeStyle="#63e6be";ctx.lineCap="butt";ctx.stroke();ctx.fillStyle="#eef5fa";ctx.textAlign="center";ctx.font="700 23px Manrope";ctx.fillText((metrics.pass||0).toFixed(1)+"%",cx,cy+2);ctx.fillStyle="#849bb1";ctx.font="9px DM Mono";ctx.fillText("PASS RATE",cx,cy+19);ctx.textAlign="left";
}
function drawCharts(filters) {const m=aggregateMetrics(filters);drawLineChart($("trendChart"),monthlyValues(filters));drawBarChart($("categoryChart"),categoryValues(filters));drawDonut($("qualityChart"),m);drawBarChart($("issueChart"),issueValues(filters));}
function filteredRecords(filters) {
  const q=$("recordSearch").value.trim().toLowerCase();
  return dashboardData.records.filter((r)=>{
    const statusMatches=filters.quality==="all"||(filters.quality==="valid"?r.is_valid:!r.is_valid);
    const basic=(filters.category==="all"||r.category===filters.category)&&(filters.region==="all"||r.region===filters.region)&&statusMatches;
    const text=[r.doc_id,r.supplier_name,r.email,r.status].filter(Boolean).join(" ").toLowerCase();
    return basic&&(!q||text.includes(q));
  });
}
function renderRecords(filters) {
  const rows=filteredRecords(filters);lastVisibleRecords=rows;const body=$("recordsBody");body.innerHTML="";
  $("recordCount").textContent=`${number(rows.length)} matching sample records`;
  if(!rows.length){const tr=document.createElement("tr");const td=document.createElement("td");td.colSpan=8;td.className="loading";td.textContent="No sample records match these filters.";tr.appendChild(td);body.appendChild(tr);return;}
  rows.slice(0,100).forEach((r)=>{const tr=document.createElement("tr");const values=[r.doc_id,r.category,r.region,r.supplier_name||"—",money(r.spend),r.status||"—",`${r.quality_score.toFixed(1)}%`,r.is_valid?"Passed":"Review"];
    values.forEach((v,i)=>{const td=document.createElement("td");td.textContent=v;if(i===0)td.className="doc-id";if(i===7){const span=document.createElement("span");span.className=`status-pill ${r.is_valid?"status-valid":"status-review"}`;span.textContent=v;td.textContent="";td.appendChild(span);}tr.appendChild(td);});body.appendChild(tr);});
  $("sampleNote").textContent=`Showing up to 100 of ${number(rows.length)} matching records from the 900-row browser sample. Full-dataset KPIs and charts use all 47,000 records.`;
}
function refresh() {const f=selected();updateKpis(f);drawCharts(f);renderRecords(f);}
function csvEscape(v){const s=v==null?"":String(v);return '"'+s.replace(/"/g,'""')+'"';}
function downloadCsv(){const rows=lastVisibleRecords;const keys=["doc_id","category","region","supplier_name","spend","status","email","quality_score","issue_count","is_valid"];const lines=[keys.join(","),...rows.map(r=>keys.map(k=>csvEscape(r[k])).join(","))];const blob=new Blob([lines.join("\n")],{type:"text/csv;charset=utf-8"});const url=URL.createObjectURL(blob);const a=document.createElement("a");a.href=url;a.download="document-intelligence-filtered-sample.csv";a.click();URL.revokeObjectURL(url);}
function initFilters(){dashboardData.categories.forEach((v)=>$("categoryFilter").add(new Option(v,v)));dashboardData.regions.forEach((v)=>$("regionFilter").add(new Option(v,v)));["categoryFilter","regionFilter","qualityFilter"].forEach(id=>$(id).addEventListener("change",refresh));$("recordSearch").addEventListener("input",()=>renderRecords(selected()));$("resetFilters").addEventListener("click",()=>{$("categoryFilter").value="all";$("regionFilter").value="all";$("qualityFilter").value="all";$("recordSearch").value="";refresh();});$("downloadCsv").addEventListener("click",downloadCsv);window.addEventListener("resize",()=>drawCharts(selected()));}
async function start(){try{const response=await fetch(DATA_URL);if(!response.ok)throw new Error(`Dataset request failed (${response.status})`);dashboardData=await response.json();initFilters();refresh();}catch(error){document.querySelector(".shell").innerHTML=`<section class="notice"><b>Dashboard data could not be loaded.</b><span>Open this site through GitHub Pages or a local web server so the browser can fetch assets/dashboard-data.json. Details: ${error.message}</span></section>`;}}
start();
